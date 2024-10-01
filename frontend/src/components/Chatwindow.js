import React, { useState, useRef } from 'react';
import { Card, List, Input, Button, Upload, Avatar, Spin } from 'antd';
import { SendOutlined, UploadOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import axios from 'axios';
import './ChatWindow.css';

const { TextArea } = Input;

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadingPDF, setIsUploadingPDF] = useState(false);
  const messagesEndRef = useRef(null);

  const handleSubmit = async () => {
    if (!inputText.trim() || isUploadingPDF) return; // Prevent submission during PDF upload

    const userMessage = {
      text: inputText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      sender: 'user',
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/rag/query', { query: inputText });
      const botMessage = {
        text: <pre style={{
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          overflow: 'auto',
          maxWidth: '100%',
        }}>
          {response.data.Response}
        </pre> || 'Sorry, I didn’t understand that.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sender: 'bot',
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error with query submission:', error);
      const errorMessage = {
        text: 'Sorry, there was an issue submitting your query.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sender: 'bot',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePDFUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file); // Append the PDF file to the FormData

    try {
      setIsUploadingPDF(true);
      const response = await axios.post('http://127.0.0.1:8000/rag/savepdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        const botMessage = {
          text: <pre style={{
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            overflow: 'auto',
            maxWidth: '100%',
          }}>
            {response.data.message}
          </pre> || 'Sorry, I didn’t understand that.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          sender: 'bot',
        };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      }
    } catch (error) {
      console.error('Error with PDF upload:', error);
      const errorMessage = {
        text: 'Sorry, there was an issue uploading the PDF.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sender: 'bot',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsUploadingPDF(false);
    }

    return false; // Prevent automatic upload
  };

  return (
    <div className="chat-container">
      <Card
        title={<div style={{ color: "white" }}>RAG Bot</div>}
        bordered={false}
        className='chat-box'
        style={{ width: 500, color: '#fff' }}
      >
        <div className="message-list-container">
          <List
            className="message-list"
            itemLayout="horizontal"
            dataSource={messages}
            renderItem={(msg, index) => (
              <List.Item
                key={index}
                className={msg.sender === 'user' ? 'user-message' : 'bot-message'}
                style={{
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <List.Item.Meta
                  avatar={
                    msg.sender === 'user' ? (
                      <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#860ff6', color: '#fff' }} />
                    ) : (
                      <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#F59E0B', color: '#fff' }} />
                    )
                  }
                  title={'You'}
                  description={<div style={{ color: "white" }}>{msg.text}<div ref={messagesEndRef}/></div>}
                  style={{
                    color: '#fff',
                    backgroundColor: msg.sender === 'user' ? '#860ff6' : '#374151',
                    borderRadius: '10px',
                    padding: '10px',
                    marginBottom: '5px',
                    maxWidth: '70%',
                  }}
                />
                <span className="message-time" style={{ color: '#D1D5DB', margin: "2px" }}>{msg.time}</span>
              </List.Item>
            )}
          />
        </div>

        {(isLoading || isUploadingPDF) && (
          <div className="loading-container">
            <Spin size="small" style={{ color: '#fff' }} />
            <span style={{ color: '#fff' }}>{isUploadingPDF ? 'Uploading PDF...' : 'Bot is typing...'}</span>
          </div>
        )}

        <TextArea
          rows={2}
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onPressEnter={handleSubmit}
          style={{
            backgroundColor: '#374151',
            color: '#fff',
            borderRadius: '5px',
            marginBottom: '10px',
          }}
          disabled={isUploadingPDF} // Disable text input during PDF upload
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          disabled={isLoading || isUploadingPDF} // Disable button while loading or uploading PDF
          style={{ width: '100%', backgroundColor: '#6b08c7', borderColor: '#1D4ED8' }}
        >
          Send
        </Button>

        <Upload
          accept=".pdf"
          showUploadList={false}
          beforeUpload={handlePDFUpload}
          style={{ marginTop: '10px' }}
        >
          <Button icon={<UploadOutlined />} style={{ width: '100%', backgroundColor: '#F59E0B' }}>
            Upload PDF
          </Button>
        </Upload>
      </Card>
    </div>
  );
};

export default ChatWindow;
