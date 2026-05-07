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
            Text(text)
                .font(.neow(.body))
                .tag(Value?.none)
            ForEach(Array(Value.allCases), id: \.self) { value in
                Text(value.rawValue)
                    .font(.neow(.body))
                    .tag(Value?.some(value))
            }
        }
        .font(.neow(.body))
        .foregroundStyle(NeowSCafeTheme.text)
        .pickerStyle(.menu)
        .buttonStyle(.bordered)
    }
}
