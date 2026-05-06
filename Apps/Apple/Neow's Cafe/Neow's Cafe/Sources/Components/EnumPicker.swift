import SwiftUI

struct EnumPicker<Value>: View
where Value: CaseIterable & Hashable & RawRepresentable,
      Value.RawValue == String
{
    let text: String
    @Binding var selection: Value?

    init(_ text: String, selection: Binding<Value?>) {
        self.text = text
        self._selection = selection
    }

    var body: some View {
        Picker(text, selection: $selection) {
            // TODO: i18n
            Text(text).tag(Value?.none)
            ForEach(Array(Value.allCases), id: \.self) { value in
                Text(value.rawValue).tag(Value?.some(value))
            }
        }
    }
}
