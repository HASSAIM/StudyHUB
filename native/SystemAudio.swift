import Foundation
import ScreenCaptureKit
import CoreMedia
import CoreGraphics
import AVFoundation
import Darwin

// Only .audio output is registered. No screen frames or microphone are recorded.
final class AudioCapture: NSObject, SCStreamOutput, SCStreamDelegate, @unchecked Sendable {
    let directory: URL
    let queue = DispatchQueue(label: "studyhub.audio")
    var stream: SCStream?
    var file: FileHandle?
    var bytes: UInt32 = 0
    var level: Float = 0
    var audioCallbacks = 0
    var screenCallbacks = 0
    var diagnostic = "waiting"
    var paused = false
    var stopping = false
    var lastSave = Date.distantPast
    var timer: DispatchSourceTimer?
    init(_ path: String) { directory = URL(fileURLWithPath: path) }
    func status(_ state: String, _ message: String = "") {
        let value: [String: Any] = ["state": state, "error": message, "audio_callbacks": audioCallbacks, "screen_callbacks": screenCallbacks, "diagnostic": diagnostic, "level": level, "bytes": bytes, "seconds": Double(bytes)/96000]
        if let data = try? JSONSerialization.data(withJSONObject: value) { try? data.write(to: directory.appendingPathComponent("native-status.json"), options: .atomic) }
    }
    func header() -> Data {
        var d = Data()
        func text(_ s: String) { d.append(s.data(using: .ascii)!) }
        func number<T: FixedWidthInteger>(_ n: T) { var v = n.littleEndian; withUnsafeBytes(of: &v) { d.append(contentsOf: $0) } }
        text("RIFF"); number(UInt32(36)+bytes); text("WAVEfmt "); number(UInt32(16)); number(UInt16(1)); number(UInt16(1)); number(UInt32(48000)); number(UInt32(96000)); number(UInt16(2)); number(UInt16(16)); text("data"); number(bytes)
        return d
    }
    func checkpoint() throws {
        guard let file else { return }
        try file.seek(toOffset: 0); try file.write(contentsOf: header()); try file.seekToEnd(); try file.synchronize()
    }
    func begin() async throws {
        status("permission")
        if !CGPreflightScreenCaptureAccess() { _ = CGRequestScreenCaptureAccess() }
        let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
        guard let display = content.displays.first else { throw NSError(domain: "StudyHUB", code: 1, userInfo: [NSLocalizedDescriptionKey:"Aucun écran disponible."]) }
        let config = SCStreamConfiguration()
        config.width = 2; config.height = 2; config.minimumFrameInterval = CMTime(value: 1, timescale: 1)
        config.capturesAudio = true; config.sampleRate = 48000; config.channelCount = 1
        config.excludesCurrentProcessAudio = false
        if #available(macOS 15.0, *) { config.captureMicrophone = false }
        let capture = SCStream(filter: SCContentFilter(display: display, excludingApplications: [], exceptingWindows: []), configuration: config, delegate: self)
        try capture.addStreamOutput(self, type: .audio, sampleHandlerQueue: queue)
        let audioURL = directory.appendingPathComponent("audio")
        FileManager.default.createFile(atPath: audioURL.path, contents: header())
        file = try FileHandle(forWritingTo: audioURL); try file?.seekToEnd()
        stream = capture
        try await capture.startCapture()
        status("recording")
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now(), repeating: .milliseconds(250))
        timer.setEventHandler { [weak self] in self?.control() }; timer.resume(); self.timer = timer
    }
    func control() {
        guard !stopping else { return }
        let url = directory.appendingPathComponent("native-control.json")
        if let data = try? Data(contentsOf: url), let object = try? JSONSerialization.jsonObject(with: data) as? [String:Any] {
            if (object["action"] as? String) == "stop" || Date().timeIntervalSince1970 - (object["lease"] as? Double ?? 0) > 180 { stopping = true; timer?.cancel(); Task { await self.finish() }; return }
            paused = (object["action"] as? String) == "pause"
        }
        do { if Date().timeIntervalSince(lastSave) > 1 { try checkpoint(); lastSave = Date() }; status(paused ? "paused" : "recording") }
        catch { stopping = true; status("error", "Impossible de sauvegarder le son : \(error.localizedDescription)"); exit(1) }
    }
    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        if type == .audio { audioCallbacks += 1 } else { screenCallbacks += 1 }
        guard type == .audio, !paused, !stopping, sampleBuffer.isValid, let desc = CMSampleBufferGetFormatDescription(sampleBuffer), let format = CMAudioFormatDescriptionGetStreamBasicDescription(desc)?.pointee else { return }
        var needed = 0
        _ = CMSampleBufferGetAudioBufferListWithRetainedBlockBuffer(sampleBuffer, bufferListSizeNeededOut: &needed, bufferListOut: nil, bufferListSize: 0, blockBufferAllocator: nil, blockBufferMemoryAllocator: nil, flags: UInt32(kCMSampleBufferFlag_AudioBufferList_Assure16ByteAlignment), blockBufferOut: nil)
        guard needed > 0 else { diagnostic = "audio-buffer-size-missing"; return }
        let memory = UnsafeMutableRawPointer.allocate(byteCount: needed, alignment: 16)
        defer { memory.deallocate() }
        let pointer = memory.bindMemory(to: AudioBufferList.self, capacity: 1)
        var block: CMBlockBuffer?
        let result = CMSampleBufferGetAudioBufferListWithRetainedBlockBuffer(sampleBuffer, bufferListSizeNeededOut: nil, bufferListOut: pointer, bufferListSize: needed, blockBufferAllocator: nil, blockBufferMemoryAllocator: nil, flags: UInt32(kCMSampleBufferFlag_AudioBufferList_Assure16ByteAlignment), blockBufferOut: &block)
        let list = UnsafeMutableAudioBufferListPointer(pointer)
        guard result == noErr, let data = list.first?.mData else { diagnostic = "audio-buffer-error: \(result), needed: \(needed)"; return }
        diagnostic = "audio-buffer-received"
        let count = CMSampleBufferGetNumSamples(sampleBuffer)
        guard format.mChannelsPerFrame == 1, format.mSampleRate == 48000 else { stopping = true; status("error", "Format audio système inattendu."); exit(1) }
        var output = Data(capacity: count * 2); var peak: Float = 0
        for i in 0..<count {
            let value: Float
            if format.mFormatFlags & kAudioFormatFlagIsFloat != 0 && format.mBitsPerChannel == 32 { value = data.assumingMemoryBound(to: Float.self)[i] }
            else if format.mBitsPerChannel == 16 { value = Float(data.assumingMemoryBound(to: Int16.self)[i])/32768 }
            else { stopping = true; status("error", "Encodage audio système inattendu."); exit(1) }
            let safe = value.isFinite ? max(-1, min(1, value)) : 0
            peak = max(peak, abs(safe)); var sample = Int16(safe * 32767).littleEndian
            withUnsafeBytes(of: &sample) { output.append(contentsOf: $0) }
        }
        do {
            guard UInt64(bytes) + UInt64(output.count) < UInt64(UInt32.max)-36 else { throw NSError(domain:"StudyHUB",code:2,userInfo:[NSLocalizedDescriptionKey:"Limite de durée audio atteinte."]) }
            try file?.write(contentsOf: output); bytes += UInt32(output.count); level = peak
        } catch { stopping = true; status("error", error.localizedDescription); exit(1) }
    }
    func stream(_ stream: SCStream, didStopWithError error: Error) { status("error", error.localizedDescription); exit(1) }
    func finish() async {
        try? await stream?.stopCapture()
        queue.sync { do { try checkpoint(); try file?.close(); file = nil; status("stopped") } catch { status("error", error.localizedDescription) } }
        exit(0)
    }
}
@main struct Main {
    static func main() async {
        guard CommandLine.arguments.count == 2 else { exit(2) }
        let capture = AudioCapture(CommandLine.arguments[1])
        do { try await capture.begin(); while true { try await Task.sleep(nanoseconds: 1_000_000_000); withExtendedLifetime(capture) {} } }
        catch { capture.status("error", "Autorise StudyHUB Audio dans Réglages Système → Confidentialité et sécurité → Enregistrement de l’écran et de l’audio système. " + error.localizedDescription); exit(1) }
    }
}
