import { useState } from 'react'
import axios from 'axios';
import './App.css'
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';




function App() {
  const [youtubeContent,setYoutubeContent] = useState("")
  const [youtubeSummary,setYoutubeSummary] = useState("")
  const [youtubeLink, setYoutubeLink] = useState("")
  const [buttonClicked, setButtonClicked] = useState(false)

  const handlePostRequest = async () => {
    setButtonClicked(true)
    setYoutubeContent("")
    setYoutubeSummary("")
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

  const handleSummarizeRequest = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/summarize', {
        // Your POST data goes here
        youtubeContent
      });

      setYoutubeSummary(response.data);

    } catch (error) {
      console.error('Error making POST request:', error);
    }
  };

  return (
    <>
      <h2>Enter YouTube URL</h2>
      <TextField id="outlined-basic" label="Youtube URL" variant="outlined" value={youtubeLink} onChange={(e)=>setYoutubeLink(e.target.value)}/>
      <Button variant="outlined" style={{margin: "12px"}} onClick={handlePostRequest}>Send</Button>
      {youtubeContent ? (
        <div>
          <p>/ - COMPLETE - /</p>
          <Button variant="outlined" style={{margin: "12px"}} onClick={handlePostRequest}>Ask Questions</Button>
          <Button variant="outlined" style={{margin: "12px"}} onClick={handleSummarizeRequest}>Summarize</Button>
          <Button variant="outlined" style={{margin: "12px"}} onClick={handlePostRequest}>Take Exam</Button>
          <div>{youtubeSummary && youtubeSummary}</div>
        </div>
        
      ) : (
        <div>
          {buttonClicked && <CircularProgress />}
        </div>  
      )}
    </>
  )
}

export default App
