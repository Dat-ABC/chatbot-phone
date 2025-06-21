import styled from "styled-components";
import ReactMarkdown from "react-markdown";
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import imageSize from 'fs-imagesize';


const MessageContainer = styled.div`
  display: flex;
  justify-content: ${(props) => (props.isUser ? 'flex-end' : 'flex-start')};
  margin: 10px 0;
`;

const Avatar = styled.div`
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${(props) => (props.isUser ? '#1a237e' : '#e0e0e0')};
  color: ${(props) => (props.isUser ? '#ffffff' : '#000000')};
  font-size: 16px;
  order: ${(props) => (props.isUser ? '1' : '0')};
`;


const MessageBubble = styled.div`
  max-width: 49%;
  padding: 10px;
  border-radius: ${(props) =>
        props.isUser ? '20px 20px 0 20px' : '20px 20px 20px 0'};
  background-color: ${(props) => (props.isUser ? '#1a237e' : '#ffffff')};
  color: ${(props) => (props.isUser ? '#ffffff' : '#000000')};
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  font-size: 16px;
  line-height: 1.5;

  p {
    margin: 0;
  }

  code {
    background-color: ${(props) => (props.isUser ? '#283593' : '#f5f5f5')};
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 14px;
  }

  pre {
    background-color: ${(props) => (props.isUser ? '#283593' : '#f5f5f5')};
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;

    code {
      background-color: transparent;
      padding: 0;
    }
  }

  ul,
  ol {
    margin: 8px 0;
    padding-left: 20px;
  }

  table {
    width: 100%;
    background: ${props => props.isUser ? 'rgba(255,255,255,0.1)' : '#f8f9fa'};
    border-radius: 8px;
    overflow: hidden;
    font-size: 15px;
    // font-family: 'Courier New', monospace;
    table-layout: fixed; /* Đảm bảo cột có chiều rộng cố định */
    word-wrap: break-word; /* Cho phép ngắt từ khi cần thiết */
  }

  th, td {
    padding: 8px;
    text-align: left;
    line-height: 1.5;
    white-space: pre-wrap; /* Giữ nguyên khoảng trắng và cho phép ngắt dòng */
    word-break: break-word; /* Ngắt từ để tránh tràn nội dung */
    border-right: 1px solid ${p => p.isUser ? 'rgba(255,255,255,0.2)' : '#dee2e6'};
    border-bottom: 1px solid ${p => p.isUser ? 'rgba(255,255,255,0.2)' : '#dee2e6'};
  }

  th {
    background: ${props => props.isUser ? 'rgba(255,255,255,0.15)' : '#e9ecef'};
    font-weight: 600;
  }
`;

// Custom renderer for images (responsive, rounded corners)
const markdownComponents = {
    img: ({ node, ...props }) => (
        <img
            {...props}
            style={{ display: 'block', maxWidth: '25%', borderRadius: '8px', margin: '8px 0' }}
            alt={props.alt}
        />
    )
};

const ChatMessage = ({ message, isUser }) => {
    // Nếu message là object { text: string }, lấy .text; nếu đã string, giữ nguyên

    // const testMd = `
    // ![Test Image](https://drive.google.com/uc?export=download&id=16IMfVJz6lOQ5coLW-bgbYHTYAz2wOfem)
    //   `;

    const messageText =
        typeof message === 'string'
            ? message
            : typeof message.text === 'string'
                ? message.text
                : JSON.stringify(message);

    // // 3. Chọn nguồn Markdown để render
    // const toRender = process.env.NODE_ENV === 'development'
    // ? testMd       // khi dev thì dùng testMd
    // : messageText; // production thì dùng messageText

    return (
        <MessageContainer isUser={isUser}>
            <Avatar isUser={isUser}>
                {isUser ? '👤' : '🤖'}
            </Avatar>
            <MessageBubble isUser={isUser}>
                <ReactMarkdown remarkPlugins={[remarkGfm, [imageSize]]} rehypePlugins={[rehypeRaw]} components={markdownComponents}>
                    {messageText}


                    {/* {
            `
            ### Bảng So Sánh iOS và Android

| Tiêu chí                  | iOS (Apple)                                               | Android (Samsung, Xiaomi, Oppo, v.v.)             |
|---------------------------|-----------------------------------------------------------|---------------------------------------------------|
| **Thiết bị**              | Chỉ iPhone, iPad, Apple sản xuất                         | Rất nhiều hãng, nhiều mẫu mã, giá đa dạng         |
| **Cập nhật phần mềm**     | Nhanh, đồng loạt, hỗ trợ 5-6 năm                         | Chậm hơn, tùy từng hãng, thường 2-4 năm           |
| **Bảo mật & riêng tư**    | Cao, kiểm soát chặt, ít malware                          | Khá tốt nhưng kém iOS, nguy cơ malware nhiều hơn  |
| **Tùy biến giao diện**    | Hạn chế, giao diện đồng bộ, ít tùy chỉnh                 | Rất linh hoạt, tùy biến mạnh                      |
| **Kho ứng dụng**          | App Store, kiểm duyệt nghiêm, chất lượng cao             | Google Play, nhiều app miễn phí, kiểm duyệt lỏng  |
| **Đa dạng sản phẩm**      | Ít mẫu, tập trung cao cấp                                | Rất nhiều mẫu, từ giá rẻ đến cao cấp              |
| **Tích hợp hệ sinh thái** | Tuyệt vời với Mac, iPad, Apple Watch, AirPods...         | Tùy từng hãng, Google dịch vụ phổ biến            |
| **Giá bán**               | Cao, ít giảm giá                                         | Đủ mọi phân khúc, dễ tiếp cận người dùng phổ thông|
| **Hỗ trợ sau bán**        | Chính hãng tốt, dễ nâng cấp                              | Tùy hãng, tùy địa phương                          |

---
`
          } */}
                </ReactMarkdown>
            </MessageBubble>
        </MessageContainer>
    );
};

/**
 * Component hiển thị một tin nhắn trong cuộc trò chuyện
 * Hỗ trợ:
 * - Hiển thị tin nhắn người dùng và bot với style khác nhau
 * - Render markdown content
 * - Style cho code blocks, tables, lists
 * 
 * @param {Object} props - Props của component
 * @param {Object} props.message - Thông tin tin nhắn
 * @param {string} props.message.text - Nội dung tin nhắn
 * @param {boolean} props.isUser - Đánh dấu tin nhắn của người dùng hay bot
 */

// const ChatMessage = ({ message, isUser }) => {
//     // Chuyển đổi tin nhắn sang string nếu chưa phải

//     const messageText = typeof message === 'string' ? message : JSON.stringify(message.text);

//     return (
//         <MessageContainer isUser={isUser}>
//             <MessageBubble isUser={isUser}>
//                 <ReactMarkdown>{messageText}</ReactMarkdown>
//             </MessageBubble>
//         </MessageContainer>
//     );
// };

export default ChatMessage;