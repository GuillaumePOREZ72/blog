import React from 'react'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import BlogList from './pages/BlogList'
import WriteBlog from './pages/WriteBlog'
import BlogDetail from './pages/BlogDetail'


function App() {
  

  return (
   <BrowserRouter>
    <Routes>
      <Route path="/" element={<BlogList/>}/>
      <Route path="/write" element={<WriteBlog/>}/>
      <Route path="/blog/:firstParam" element={<BlogDetail/>}/>
    </Routes>
   </BrowserRouter>
  )
}

export default App
