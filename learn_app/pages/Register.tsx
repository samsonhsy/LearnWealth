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
        interests: "",
    });

    const toggleForm = (field: keyof RegisterForm, value: string) => {
        setForm({
            ...form,
            [field]: value,
        });
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

    const handleSubmit=async() =>{
        console.log("Submitting registration form:", form);

        if (form.interests.trim() === "") {
            notify('Please enter your interests', 'error');
            return;
        }

        const newUser = {
          username: form.username,
          email: form.email,
          password: form.password,
          interests: form.interests,
        };
        try{
              const response = await axios.post("https://ctflife-demo.zeabur.app/users/", newUser);
              notify('User Registered Successfully', 'success');
            } catch(error){
              console.error("Error occurred when registering user", error);
              notify('User Was Not Registered', 'error');
          }
    };

    return( 
        <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-900 text-white">
            <div className="w-full max-w-md ">
                {!isInterest && <UserInfo handleUserInfo={handleUserInfo} form={form} toggleForm={toggleForm} />}
                {isInterest && <Interest View={View} toggleView={toggleView}/>}
            </div>
        </div>

    
    );
}