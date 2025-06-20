// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "WisbeeRAG",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    dependencies: [
        .package(url: "https://github.com/buhe/langchain-swift", branch: "main"),
        .package(url: "https://github.com/objectbox/objectbox-swift", from: "1.9.2")
    ],
    targets: [
        .executableTarget(
            name: "WisbeeRAG",
            dependencies: [
                .product(name: "LangChain", package: "langchain-swift"),
                .product(name: "ObjectBox", package: "objectbox-swift")
            ]
        ),
    ]
)
