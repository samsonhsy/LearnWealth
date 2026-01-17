import { Button, ButtonGroup, TextField } from "@mui/material";
import { ChessQueen, Crown, FlaskConical, Headset, Palette } from "lucide-react";

export default function Interest(props) {
    const {handleSubmit, form, toggleForm, toggleFormInterest} = props;
    return(
        <div >
            <div className="text-2xl font-bold mb-4 text-center">
                <span>What is your interest?</span>
            </div>
            <div className="w-full rounded-3xl shadow-2xl p-8 bg-white text-gray-800 border-0 mt-6">
                <form className = "flex flex-col gap-4" onSubmit={handleSubmit}>
                    <ButtonGroup orientation="vertical" aria-label="Vertical button group" >
                        <Button  
                            style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} 
                            className="grid grid-cols-2 gap-4 w-full"
                            onClick={() => toggleFormInterest("Gaming")}
                            variant={form.interests.includes("Gaming") ? "contained" : "text"}>
                            <Headset />
                            <div>Gaming</div>
                        </Button>
                        <Button 
                            style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} 
                            className="grid grid-cols-2 gap-4 w-full"
                            onClick={() => toggleFormInterest("Science")}
                            variant={form.interests.includes("Science") ? "contained" : "text"}>
                            <FlaskConical />
                            <div>
                                Science
                            </div>
                        </Button>
                        <Button 
                            style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} 
                            className="grid grid-cols-2 gap-4 w-full"
                            onClick={() => toggleFormInterest("Arts")}
                            variant={form.interests.includes("Arts") ? "contained" : "text"}>
                            <Palette />
                            <div>
                                Arts
                            </div>
                        </Button>
                        <Button 
                            style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} 
                            className="grid grid-cols-2 gap-4 w-full"
                            onClick={() => toggleFormInterest("Western History")}
                            variant={form.interests.includes("Western History") ? "contained" : "text"}>
                            <ChessQueen />
                            <div>
                                Western History
                            </div>
                        </Button>
                        <Button 
                            style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} 
                            className="grid grid-cols-2 gap-4 w-full"
                            onClick={() => toggleFormInterest("Chinese History")}
                            variant={form.interests.includes("Chinese History") ? "contained" : "text"}>
                            <Crown />
                            <div>
                                Chinese History
                            </div> 
                        </Button>
                    </ButtonGroup>
                    <TextField 
                        style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px'}} 
                        id="standard-basic" 
                        label="Other..." 
                        variant="standard"
                        onChange={e => toggleForm("otherInterest", e.target.value)}
                        >
                    </TextField>
                    <div className="mt-6">
                        <Button 
                            variant="contained" 
                            className="w-full text-white py-4 rounded-2xl font-bold shadow-lg shadow-teal-600/20 transition"
                            type="submit"
                            >Done!</Button>
                    </div>
                </form>
            </div>
        </div>
    );
        
}