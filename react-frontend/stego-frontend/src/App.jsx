import React, { useState } from 'react';

function App() {
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    backgroundColor: '#f0f4f8',
    minHeight: '100vh',
    minWidth: '100vw',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };

  const cardStyle = {
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    padding: '60px',
    margin: '20px',
    width: '100%',
    maxWidth: '500px',
  };

  const headerStyle = {
    textAlign: 'center',
    color: '#333',
    marginBottom: '20px',
  };

  const inputStyle = {
    width: '100%',
    padding: '10px',
    margin: '10px 0',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '16px',
  };

  const buttonStyle = {
    backgroundColor: '#1976d2',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '10px',
  };

  const [encodeFile, setEncodeFile] = useState(null);
  const [encodeMessage, setEncodeMessage] = useState('');
  const [encodePassword, setEncodePassword] = useState('');

  const [decodePassword, setDecodePassword] = useState('');
  const [decodedMessage, setDecodedMessage] = useState('');

  const handleEncodeSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', encodeFile);
    formData.append('message', encodeMessage);
    formData.append('password', encodePassword);

    try {
      const response = await fetch('http://127.0.0.1:8000/encode', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        alert(data.message);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error during encoding:', error);
      alert('Error during encoding');
    }
  };

  const handleDecodeSubmit = async (e) => {
    e.preventDefault();
    if (!decodePassword) {
      alert('Please provide a password.');
      return;
    }
    const formData = new FormData();
    formData.append('password', decodePassword);

    try {
      const response = await fetch('http://127.0.0.1:8000/decode', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setDecodedMessage(data.message);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error during decoding:', error);
      alert('Error during decoding');
    }
  };

  return (
    <div style={containerStyle}>
      <h1 style={headerStyle}>Steganography Tool</h1>

      {/* Encode Section */}
      <div style={cardStyle}>
        <h2 style={headerStyle}>Encode a Message into an Image</h2>
        <form onSubmit={handleEncodeSubmit}>
          <div>
            <label>Image File (PNG):</label>
            <input
              style={inputStyle}
              type='file'
              accept='image/png'
              onChange={(e) => setEncodeFile(e.target.files[0])}
            />
          </div>
          <div>
            <label>Message:</label>
            <input
              style={inputStyle}
              type='text'
              value={encodeMessage}
              onChange={(e) => setEncodeMessage(e.target.value)}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              style={inputStyle}
              type='password'
              value={encodePassword}
              onChange={(e) => setEncodePassword(e.target.value)}
            />
          </div>
          <button style={buttonStyle} type='submit'>
            Encode
          </button>
        </form>
      </div>

      {/* Decode Section */}
      <div style={cardStyle}>
        <h2 style={headerStyle}>Decode a Message from stego.png</h2>
        <form onSubmit={handleDecodeSubmit}>
          <div>
            <label>Password:</label>
            <input
              style={inputStyle}
              type='password'
              value={decodePassword}
              onChange={(e) => setDecodePassword(e.target.value)}
            />
          </div>
          <button style={buttonStyle} type='submit'>
            Decode
          </button>
        </form>
        {decodedMessage && (
          <div
            style={{ marginTop: '20px', textAlign: 'center', color: '#333' }}
          >
            <h3>Decoded Message:</h3>
            <p>{decodedMessage}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
