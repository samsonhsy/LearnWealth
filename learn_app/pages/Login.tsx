import { INITIAL_USER } from '@/App';
import { User, View } from '@/types';
import { colors } from '@mui/material';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from './logo.png';
import { Scale } from 'lucide-react';

export default function LoginView(props) {
    const { View, setView, handleLogin, toggleLogInForm, loginForm } = props;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-900 text-white">
      <div className="w-full max-w-md bg-white text-gray-800 rounded-3xl shadow-2xl p-8">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-teal-600 rounded-2xl flex items-center justify-center text-white font-black text-2xl overflow-hidden"><img src={Logo} className='scale-150 transform-gpu' alt="app logo" /></div>
        </div>
        <div className="text-2xl font-bold text-center mb-2">因財C教</div>
        <h1 className="text-2xl font-bold text-center mb-2">Welcome Back</h1>
        <p className="text-center text-gray-500 mb-8 text-sm">Empowering your financial future</p>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <input 
            type="text" 
            placeholder="Email"
            value={loginForm.email}
            onChange={(e) => toggleLogInForm('email', e.target.value)}
            className="w-full p-4 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-teal-500 transition outline-none"
          />
          <input 
            type="password" 
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) => toggleLogInForm('password', e.target.value)}
            className="w-full p-4 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-teal-500 outline-none"
          />

          <Button variant="contained" 
                  className="w-full text-white py-4 rounded-2xl font-bold shadow-lg shadow-teal-600/20 transition"
                  type='submit'
          >Sign In</Button>
        </form>

        <button onClick={() => props.toggleView(View.REGISTER)} style={{color: "#1976d2"}} className="w-full mt-6 text-sm font-medium hover:underline">
            "Don't have an account? Sign up"
        </button>
      </div>
    </div>
  );}
