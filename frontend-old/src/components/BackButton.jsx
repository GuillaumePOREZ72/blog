import React from 'react'
import { useNavigate } from 'react-router-dom'
import { IoArrowBack } from 'react-icons/io5'

export default function BackButton() {
      const navigate = useNavigate()
  return (
    <button 
      onClick={() => navigate('/')}
      className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors" >
      <IoArrowBack className='w-5 h-5'/>
      <span>Back</span>
    </button>
  )
}
