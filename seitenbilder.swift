// PDF-Seiten als JPEG speichern (lokal, nur macOS): swift seitenbilder.swift datei.pdf zielordner [skala]
// Schreibt zielordner/1.jpg, 2.jpg, … (Skala 2 ≈ 144 dpi). Für trump_laden.py: Seitenbilder für ein Bild-Sprachmodell.
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: args[1]))!
let ziel = URL(fileURLWithPath: args[2])
let skala: CGFloat = args.count > 3 ? CGFloat(Double(args[3])!) : 2
try FileManager.default.createDirectory(at: ziel, withIntermediateDirectories: true)
for i in 0..<doc.pageCount {
    let seite = doc.page(at: i)!
    let rahmen = seite.bounds(for: .mediaBox)
    let bild = NSImage(size: NSSize(width: rahmen.width * skala, height: rahmen.height * skala))
    bild.lockFocus()
    NSColor.white.set()
    NSRect(origin: .zero, size: bild.size).fill()
    let ctx = NSGraphicsContext.current!.cgContext
    ctx.scaleBy(x: skala, y: skala)
    seite.draw(with: .mediaBox, to: ctx)
    bild.unlockFocus()
    let rep = NSBitmapImageRep(data: bild.tiffRepresentation!)!
    let jpg = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.8])!
    try jpg.write(to: ziel.appendingPathComponent("\(i + 1).jpg"))
}
print(doc.pageCount)
