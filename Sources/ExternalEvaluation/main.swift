import Foundation
import OfferCore

struct Row {
    let caseHash: String
    let gold: SpendingCategory
    let description: String
}

let goldCategories: [SpendingCategory] = [.groceries, .dining, .transport, .shopping, .utilities]
let predictedCategories: [SpendingCategory] = goldCategories + [.unknown]
let policyNames = ["metadata", "tokens", "combined", "conflict_abstain"]

func csv(_ value: String) -> String {
    "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
}
func parseCategory(_ raw: String) -> SpendingCategory? {
    SpendingCategory(rawValue: raw)
}
func metrics(truth: [SpendingCategory], predicted: [SpendingCategory]) -> (Int, Int, Int, Int, Double, Double?, Double) {
    let correct = zip(truth, predicted).filter { $0.0 == $0.1 }.count
    let covered = predicted.filter { $0 != .unknown }.count
    let conditional = zip(truth, predicted).filter { $0.1 != .unknown }
    let conditionalCorrect = conditional.filter { $0.0 == $0.1 }.count
    let perClassF1 = goldCategories.map { category -> Double in
        var tp = 0, fp = 0, fn = 0
        for (g,p) in zip(truth,predicted) {
            if g == category && p == category { tp += 1 }
            if g != category && p == category { fp += 1 }
            if g == category && p != category { fn += 1 }
        }
        let denominator = 2 * tp + fp + fn
        return denominator == 0 ? 0 : Double(2 * tp) / Double(denominator)
    }
    let macro = perClassF1.reduce(0,+) / Double(goldCategories.count)
    let n = truth.count
    return (n, correct, covered, conditional.count,
            n == 0 ? 0 : Double(correct)/Double(n),
            covered == 0 ? nil : Double(conditionalCorrect)/Double(covered), macro)
}

let args = CommandLine.arguments
if args.count != 3 {
    fputs("usage: external-evaluation <prepared.tsv> <results-directory>\n", stderr)
    exit(64)
}
let inputURL = URL(fileURLWithPath: args[1])
let resultsURL = URL(fileURLWithPath: args[2], isDirectory: true)
try FileManager.default.createDirectory(at: resultsURL, withIntermediateDirectories: true)
let text = try String(contentsOf: inputURL, encoding: .utf8)
var rows: [Row] = []
for (lineNumber, line) in text.split(whereSeparator: \.isNewline).enumerated() {
    let fields = line.split(separator: "\t", omittingEmptySubsequences: false)
    guard fields.count == 3,
          let gold = parseCategory(String(fields[1])), gold != .unknown,
          let bytes = Data(base64Encoded: String(fields[2])),
          let description = String(data: bytes, encoding: .utf8) else {
        fatalError("Invalid prepared row at line \(lineNumber + 1)")
    }
    rows.append(Row(caseHash: String(fields[0]), gold: gold, description: description))
}
guard !rows.isEmpty else { fatalError("No mapped evaluation rows") }

let classifier = Classifier()
var rowPredictions: [String: [SpendingCategory]] = [:]
var rowTruth: [SpendingCategory] = []
var caseGroups: [String: (gold: SpendingCategory?, description: String)] = [:]
for (index, row) in rows.enumerated() {
    // The external file's labels are kept out of Transaction and classifier input.
    let transaction = Transaction(id: "external-\(index)", accountID: "external", currency: "GBP",
                                  description: row.description, merchantID: nil, structuredCategory: nil)
    let predictions: [(String, SpendingCategory)] = [
        ("metadata", classifier.classify(transaction, method: .metadata).category),
        ("tokens", classifier.classify(transaction, method: .tokens).category),
        ("combined", classifier.classify(transaction, method: .combined).category),
        ("conflict_abstain", ConflictAware.classify(transaction).category)
    ]
    for (name, prediction) in predictions { rowPredictions[name, default: []].append(prediction) }
    rowTruth.append(row.gold)
    if let previous = caseGroups[row.caseHash] {
        if previous.gold != row.gold { caseGroups[row.caseHash] = (nil, previous.description) }
    } else {
        caseGroups[row.caseHash] = (row.gold, row.description)
    }
}

var caseTruth: [SpendingCategory] = []
var caseRows: [Row] = []
for (hash, group) in caseGroups.sorted(by: { $0.key < $1.key }) {
    if let gold = group.gold { caseTruth.append(gold); caseRows.append(Row(caseHash: hash, gold: gold, description: group.description)) }
}
var casePredictions: [String: [SpendingCategory]] = [:]
for (index, row) in caseRows.enumerated() {
    let transaction = Transaction(id: "unique-description-\(index)", accountID: "external", currency: "GBP",
                                  description: row.description, merchantID: nil, structuredCategory: nil)
    casePredictions["metadata", default: []].append(classifier.classify(transaction, method: .metadata).category)
    casePredictions["tokens", default: []].append(classifier.classify(transaction, method: .tokens).category)
    casePredictions["combined", default: []].append(classifier.classify(transaction, method: .combined).category)
    casePredictions["conflict_abstain", default: []].append(ConflictAware.classify(transaction).category)
}

var confusion = "policy,unit,gold,predicted,count\n"
var summary = "policy,unit,n,correct,accuracy,covered,coverage,abstained,abstention_rate,classified_correct,classified_n,classified_only_accuracy,macro_f1\n"
var perClass = "policy,unit,class,tp,fp,fn,support,precision,recall,f1\n"
for policy in policyNames {
    for (unit, truth, preds) in [("transactions", rowTruth, rowPredictions[policy]!), ("unique_descriptions", caseTruth, casePredictions[policy]!)] {
        for gold in goldCategories {
            for predicted in predictedCategories {
                let count = zip(truth, preds).filter { $0.0 == gold && $0.1 == predicted }.count
                confusion += "\(policy),\(unit),\(gold.rawValue),\(predicted.rawValue),\(count)\n"
            }
        }
        let (n, correct, covered, classifiedN, accuracy, classifiedAccuracy, macroF1) = metrics(truth: truth, predicted: preds)
        let classifiedOnlyText = classifiedAccuracy.map { String($0) } ?? "NA"
        let classifiedCorrect = zip(truth,preds).filter { $0.1 != .unknown && $0.0 == $0.1 }.count
        let abstained = n - covered
        summary += "\(policy),\(unit),\(n),\(correct),\(accuracy),\(covered),\(n == 0 ? 0 : Double(covered)/Double(n)),\(abstained),\(n == 0 ? 0 : Double(abstained)/Double(n)),\(classifiedCorrect),\(classifiedN),\(classifiedOnlyText),\(macroF1)\n"
        for category in goldCategories {
            var tp = 0, fp = 0, fn = 0
            for (g,p) in zip(truth,preds) {
                if g == category && p == category { tp += 1 }
                if g != category && p == category { fp += 1 }
                if g == category && p != category { fn += 1 }
            }
            let support = tp + fn
            let precision = tp + fp == 0 ? 0 : Double(tp)/Double(tp+fp)
            let recall = support == 0 ? 0 : Double(tp)/Double(support)
            let f1den = 2*tp+fp+fn
            let f1 = f1den == 0 ? 0 : Double(2*tp)/Double(f1den)
            perClass += "\(policy),\(unit),\(category.rawValue),\(tp),\(fp),\(fn),\(support),\(precision),\(recall),\(f1)\n"
        }
    }
}
try confusion.write(to: resultsURL.appendingPathComponent("confusion.csv"), atomically: true, encoding: .utf8)
try summary.write(to: resultsURL.appendingPathComponent("summary.csv"), atomically: true, encoding: .utf8)
try perClass.write(to: resultsURL.appendingPathComponent("per-class.csv"), atomically: true, encoding: .utf8)
print("evaluated_rows=\(rows.count)")
print("unique_unanimous_descriptions=\(caseRows.count)")
print("policies=\(policyNames.joined(separator: ","))")
print("rows_and_unique_description_metrics_written_without_raw_descriptions=true")
