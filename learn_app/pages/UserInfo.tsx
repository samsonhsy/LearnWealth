import { Button, TextField } from "@mui/material";

export default function UserInfo(porps) {
    const {handleUserInfo, form, toggleForm} = porps;
    return(
        <div >
            <div className="text-2xl font-bold mb-4 text-center">
                <span>Register Your Acount!</span>
                <br/>
                <span>Kick Start Your Financial Journey!</span>
            </div>
            <div className="w-full rounded-3xl shadow-2xl p-8 bg-white text-gray-800 border-0  mt-6">
                <form className = "flex flex-col gap-4 outline-none">
                    <TextField
                        required
                        label = "Username"
                        variant="standard"
                        id = "margin-dense"
                        type="text" 
                        value={form.username}
                        onChange={e => toggleForm("username", e.target.value)}
                    />
                    <TextField
                        required
                        label = "Email Address"
                        variant="standard"
                        id = "margin-dense"
                        type="text" 
                        value={form.email}
                        onChange={e => toggleForm("email", e.target.value)}
                    />
                    <TextField
                        required
                        label = "Password"
                        variant="standard"
                        id = "margin-dense"
                        type="text" 
                        value={form.password}
                        onChange={e => toggleForm("password", e.target.value)}
                    /> 
                    <TextField
                        required
                        label = "Confirm Password Again"
                        variant="standard"
                        id = "margin-dense"
                        type="text" 
                        value={form.confirmPassword}
                        onChange={e => toggleForm("confirmPassword", e.target.value)}
                    /> 
                    <div className="mt-6">
                        <Button 
                            variant="contained" 
                            onClick ={() => handleUserInfo(event)}
                            className="w-full text-white py-4 rounded-2xl font-bold shadow-lg shadow-teal-600/20 transition"
                        >Continue</Button>
                    </div>
                </form>
            </div>

        </div>
    );
        
}