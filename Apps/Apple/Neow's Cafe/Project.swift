import ProjectDescription

let project = Project(
    name: "Neow's Cafe",
    targets: [
        .target(
            name: "Neow's Cafe",
            destinations: .iOS,
            product: .app,
            bundleId: "io.clooney.apple.Neow-s-Cafe",
            infoPlist: .extendingDefault(
                with: [
                    "UILaunchScreen": [
                        "UIColorName": "",
                        "UIImageName": "",
                    ],
                    "UIAppFonts": [
                        "kreon_regular.ttf",
                        "kreon_bold.ttf",
                    ],
                ]
            ),
            buildableFolders: [
                "Neow's Cafe/Sources",
                "Neow's Cafe/Resources",
            ],
            dependencies: []
        ),
        .target(
            name: "Neow's CafeTests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "io.clooney.apple.Neow-s-CafeTests",
            infoPlist: .default,
            buildableFolders: [
                "Neow's Cafe/Tests"
            ],
            dependencies: [.target(name: "Neow's Cafe")]
        ),
    ]
)
