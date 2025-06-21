const API_URL = process.env.API_URL || 'http://localhost:8030';

/**
 * Service xử lý các tương tác chat với backend
 */

export const chatService = {
    /**
        * Gửi tin nhắn đến server và nhận phản hồi một lần
        *
        * @param {string} message - Nội dung tin nhắn cần gửi
        * @param {string} sessionId - ID phiên chat
        * @param {function} onChunk - Callback xử lý khi nhận được phản hồi
        * @returns {Promise<string>} Phản hồi từ server
    */
    sendMessage: async (message, sessionId, onChunk = (chunk) => {}) => {
        try {
            const respone = await fetch(`${API_URL}/api/chat/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    thread_id: sessionId,
                }),
            });

            if (!respone.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await respone.json();
            onChunk(data.answer);
            return data.answer;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    /**
         * Gửi tin nhắn đến server và nhận phản hồi dạng stream
         *
         * @param {string} message - Nội dung tin nhắn cần gửi
         * @param {string} sessionId - ID phiên chat
         * @param {function} onToken - Callback xử lý từng token nhận được
         * @param {function} onError - Callback xử lý khi có lỗi
     */

    sendMessageStream: async (
        message, // Nội dung tin nhắn từ người dùng
        sessionId, // ID của phiên chat hiện tại
        onToken = (token) => {}, // Callback được gọi mỗi khi nhận được token mới
        onError = (error) => {} // Callback được gọi khi có lỗi xảy ra
    ) => {
        try {
            const response = await fetch(`${API_URL}/api/chat/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    thread_id: sessionId,
                }),
            })

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Khởi tạo reader để đọc dữ liệu stream
            const reader = response.body.getReader();

            // Khởi tạo decoder để giải mã dữ liệu
            const decoder = new TextDecoder();

            while (true) {
                // Đọc dữ liệu từ stream
                const { done, value } = await reader.read();

                // Nếu không còn dữ liệu để đọc, thoát khỏi vòng lặp
                if (done) {
                    break;
                }

                // Giải mã dữ liệu và chuyển đổi thành chuỗi
                const chunk = decoder.decode(value, { stream: true });
                
                // Tách chunk thành các dòng và lọc
                // - Loại bỏ dòng trống
                // - Chỉ lấy dòng bắt đầu bằng "data: "

                const lines = chunk.split('\n').filter(line => line.trim() !== '' && line.startsWith('data: '));

                // Xử lý từng dòng SSE (Server-Sent Events)
                for (const line of lines) {
                    try {
                        // Bỏ prefix "data: " và parse JSON
                        const jsonStr = line.replace('data: ', '');
                        const json = JSON.parse(jsonStr);

                        // Kiểm tra nếu server trả về lỗi
                        if (json.error) {
                            onError(json.error); // Gọi callback xử lý lỗi
                            return;
                        }

                        // Nếu có nội dung, gửi token đến UI qua callback
                        if (json.content) {
                            // Gọi callback onToken với nội dung trả về
                            onToken(json.content);
                        }
                    } catch (error) {
                        // Nếu có lỗi trong quá trình xử lý dòng, gọi callback onError
                        console.error("Error parsing SSE message:", error);
                        onError(error);
                    }
                }
            }
        }
        catch (error) {
            // Nếu có lỗi trong quá trình gửi tin nhắn hoặc nhận phản hồi, gọi callback onError
            // Xử lý các lỗi khác (network, stream, etc.)
            console.error('Error sending message:', error);
            onError(error.message); // Thông báo lỗi cho UI
        }
    }
}
