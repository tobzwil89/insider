// Texterkennung mit Apple Vision (lokal, kostenlos, nur macOS): swift ocr.swift datei.pdf [seite]
// Gibt je erkanntem Textstück eine Zeile aus: Seite <TAB> y-Mitte <TAB> x-links <TAB> Höhe <TAB> Text
// (Werte 0–1, y von unten). Die Positionen braucht trump_laden.py, um Tabellenzeilen wieder zusammenzusetzen.
import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: args[1]))!
let seiten = args.count > 2 ? [Int(args[2])! - 1] : Array(0..<doc.pageCount)
for i in seiten {
    let seite = doc.page(at: i)!
    let rahmen = seite.bounds(for: .mediaBox)
    let skala: CGFloat = 3  // ~216 dpi
    let bild = NSImage(size: NSSize(width: rahmen.width * skala, height: rahmen.height * skala))
    bild.lockFocus()
    NSColor.white.set()
    NSRect(origin: .zero, size: bild.size).fill()
    let ctx = NSGraphicsContext.current!.cgContext
    ctx.scaleBy(x: skala, y: skala)
    seite.draw(with: .mediaBox, to: ctx)
    bild.unlockFocus()
    let cg = bild.cgImage(forProposedRect: nil, context: nil, hints: nil)!
    let anfrage = VNRecognizeTextRequest()
    anfrage.recognitionLevel = .accurate
    anfrage.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: cg).perform([anfrage])
    for b in anfrage.results ?? [] {
        guard let t = b.topCandidates(1).first?.string else { continue }
        let r = b.boundingBox
        print("\(i + 1)\t\(r.midY)\t\(r.minX)\t\(r.height)\t\(t.replacingOccurrences(of: "\t", with: " "))")
    }
}
