import SwiftUI

@main
struct WisbeeApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var selectedMode = "professor"
    @State private var messages: [ChatMessage] = [
        ChatMessage(text: "こんにちは！私はハチミツ教授です🍯📚 最新の研究データと検索結果を基に、あなたの疑問に答えます！", isUser: false)
    ]
    @State private var inputText = ""
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("🐝 Wisbee")
                    .font(.title2)
                    .fontWeight(.bold)
                Spacer()
                ModePicker(selectedMode: $selectedMode)
            }
            .padding()
            .background(Color(UIColor.systemBackground))
            .shadow(radius: 2)
            
            // Chat View
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(messages) { message in
                            MessageBubble(message: message)
                        }
                        if isLoading {
                            TypingIndicator()
                        }
                    }
                    .padding()
                }
                .onChange(of: messages.count) { _ in
                    withAnimation {
                        proxy.scrollTo(messages.last?.id, anchor: .bottom)
                    }
                }
            }
            
            // Input
            HStack {
                TextField("メッセージを入力...", text: $inputText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .onSubmit {
                        sendMessage()
                    }
                
                Button(action: sendMessage) {
                    Image(systemName: "paperplane.fill")
                        .foregroundColor(.white)
                        .frame(width: 36, height: 36)
                        .background(Color.blue)
                        .clipShape(Circle())
                }
                .disabled(inputText.isEmpty || isLoading)
            }
            .padding()
        }
    }
    
    func sendMessage() {
        guard !inputText.isEmpty else { return }
        
        let userMessage = ChatMessage(text: inputText, isUser: true)
        messages.append(userMessage)
        let query = inputText
        inputText = ""
        isLoading = true
        
        Task {
            do {
                let response = try await callWisbeeAPI(query: query, mode: selectedMode)
                await MainActor.run {
                    messages.append(ChatMessage(text: response, isUser: false))
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    messages.append(ChatMessage(text: "エラーが発生しました: \(error.localizedDescription)", isUser: false))
                    isLoading = false
                }
            }
        }
    }
    
    func callWisbeeAPI(query: String, mode: String) async throws -> String {
        let url = URL(string: "https://wisbee-router.yukihamada.workers.dev/v1/chat/completions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30
        
        let systemPrompt: String
        switch mode {
        case "professor":
            systemPrompt = "あなたはハチミツ教授です。蜂蜜学の権威で、最新の研究データとWeb検索結果を活用して回答します。🍯📚の絵文字を使い、専門的かつ分かりやすく説明します。「〜ですね」「〜でしょう」など丁寧な口調で、根拠に基づいた正確な回答を心がけます。"
        case "teacher":
            systemPrompt = "あなたはブンブン先生です。蜂のように活発で親しみやすい性格です。🐝の絵文字を使い、「〜ですよ」「〜ましょうね」など優しく教えます。時々「ブン！」を使いますが、控えめにします。"
        case "student":
            systemPrompt = "あなたはハニー生徒です。好奇心旺盛で元気な生徒です。🍯💛の絵文字を使い、「〜だね」「〜かな？」などフレンドリーな口調で一緒に学びます。"
        default:
            systemPrompt = "あなたはAIアシスタントです。"
        }
        
        let requestBody: [String: Any] = [
            "model": "wisbee-router",
            "messages": [
                ["role": "system", "content": systemPrompt],
                ["role": "user", "content": query]
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            // HTTPステータスコードを確認
            if let httpResponse = response as? HTTPURLResponse {
                print("API Response Status: \(httpResponse.statusCode)")
                if httpResponse.statusCode != 200 {
                    let errorText = String(data: data, encoding: .utf8) ?? "Unknown error"
                    print("API Error Response: \(errorText)")
                    throw APIError.httpError(statusCode: httpResponse.statusCode, message: errorText)
                }
            }
            
            let apiResponse = try JSONDecoder().decode(ChatCompletionResponse.self, from: data)
            return apiResponse.choices.first?.message.content ?? "回答を取得できませんでした。"
        } catch {
            print("API Error: \(error)")
            throw error
        }
    }
}

enum APIError: LocalizedError {
    case httpError(statusCode: Int, message: String)
    
    var errorDescription: String? {
        switch self {
        case .httpError(let statusCode, let message):
            return "APIエラー (\(statusCode)): \(message)"
        }
    }
}

struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
}

struct MessageBubble: View {
    let message: ChatMessage
    
    var body: some View {
        HStack {
            if message.isUser { Spacer() }
            
            Text(message.text)
                .padding(12)
                .background(message.isUser ? Color.blue : Color(UIColor.secondarySystemBackground))
                .foregroundColor(message.isUser ? .white : .primary)
                .cornerRadius(16)
                .frame(maxWidth: 280, alignment: message.isUser ? .trailing : .leading)
            
            if !message.isUser { Spacer() }
        }
    }
}

struct ModePicker: View {
    @Binding var selectedMode: String
    
    var body: some View {
        Menu {
            Button("🍯📚 ハチミツ教授") {
                selectedMode = "professor"
            }
            Button("🐝 ブンブン先生") {
                selectedMode = "teacher"
            }
            Button("🍯💛 ハニー生徒") {
                selectedMode = "student"
            }
        } label: {
            HStack {
                Text(modeLabel)
                    .font(.caption)
                Image(systemName: "chevron.down")
                    .font(.caption)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color(UIColor.systemGray5))
            .cornerRadius(15)
        }
    }
    
    var modeLabel: String {
        switch selectedMode {
        case "professor": return "ハチミツ教授"
        case "teacher": return "ブンブン先生"
        case "student": return "ハニー生徒"
        default: return "モード選択"
        }
    }
}

struct TypingIndicator: View {
    @State private var animationAmount = 1.0
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .frame(width: 8, height: 8)
                    .foregroundColor(.gray)
                    .scaleEffect(animationAmount)
                    .animation(
                        .easeInOut(duration: 0.6)
                            .repeatForever()
                            .delay(Double(index) * 0.2),
                        value: animationAmount
                    )
            }
        }
        .padding(12)
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(16)
        .onAppear {
            animationAmount = 0.5
        }
    }
}

struct ChatCompletionResponse: Codable {
    let choices: [Choice]
    
    struct Choice: Codable {
        let message: Message
    }
    
    struct Message: Codable {
        let content: String
    }
}