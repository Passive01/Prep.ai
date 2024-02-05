import { useState } from 'react'
import axios from 'axios';
import './App.css'
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';



function App() {
  const [youtubeContent,setYoutubeContent] = useState("")
  const [youtubeLink, setYoutubeLink] = useState("")

  const handlePostRequest = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/', {
        // Your POST data goes here
        youtubeLink
      });

      setYoutubeContent(response.data);
    } catch (error) {
      console.error('Error making POST request:', error);
    }
  };

  return (
    <>
      <h2>Enter YouTube URL</h2>
      <TextField id="outlined-basic" label="Youtube URL" variant="outlined" value={youtubeLink} onChange={(e)=>setYoutubeLink(e.target.value)}/>
      <Button variant="outlined" style={{margin: "12px"}} onClick={handlePostRequest}>Send</Button>
      {youtubeContent && (
        <div>
          <h2>Response Data:</h2>
          <b>{youtubeContent}</b>
        </div>
      )}
    </>
  )
}

export default App
