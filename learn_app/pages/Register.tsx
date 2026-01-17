import { use, useState } from "react";
import Interest from "./Interest";
import UserInfo from "./UserInfo";
import axios from "axios";
import { RegisterForm } from "@/types";

export default function Register(props) {
    const {View, toggleView, notify} = props;
    const [isInterest, setIsInterest] = useState(false);
    const toggleButton = () => {
        setIsInterest(!isInterest);
    }

    const [form, setForm] = useState<RegisterForm>({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        interests: [],
        otherInterest: "",
    });

    const toggleForm = (field: keyof RegisterForm, value: string) => {
        setForm({
            ...form,
            [field]: value,
        });
    }

    const toggleFormInterest = (value: string) => {
        if (form.interests.includes(value)) {  
            setForm({
                ...form,
                interests: form.interests.filter(item => item !== value),
            });
        }
        else
        {        
            setForm({
                ...form,
                interests: [...form.interests, value],
            });
        }
    }

    const handleUserInfo = (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.username || !form.email || !form.password) {
            notify('Please fill in all required fields', 'error');
            return;
        }
        if (form.password !== form.confirmPassword) {
            notify('Passwords do not match', 'error');
            return;
        }
        toggleButton();
    };

    console.log("Register form data:", form);

    const handleSubmit=async(e) =>{
        e.preventDefault();
        if (form.otherInterest && !form.interests.includes(form.otherInterest)) {
            toggleFormInterest(form.otherInterest);
        }
        console.log("Submitting registration form:", form);

        if (form.interests.length === 0) {
            notify('Please enter your interests', 'error');
            return;
        }

        const newUser = {
          username: form.username,
          email: form.email,
          password: form.password,
          interests: form.interests.join(","),
        };
        try{
              const response = await axios.post("/users/register", newUser); 
              console.log("User registered successfully:", response.data);
              const data = response.data;

              notify('User Registered Successfully', 'success');
              toggleView(View.LOGIN);
            } catch(error){
              console.error("Error occurred when registering user", error);
              notify('Registration failed. Please try again.', 'error');
          }
    };

    return( 
        <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-900 text-white">
            <div className="w-full max-w-md ">
                {!isInterest && <UserInfo handleUserInfo={handleUserInfo} form={form} toggleForm={toggleForm} />}
                {isInterest && <Interest handleSubmit={handleSubmit} form={form} toggleForm={toggleForm} toggleFormInterest={toggleFormInterest}/>}
            </div>
        </div>

    
    );
}