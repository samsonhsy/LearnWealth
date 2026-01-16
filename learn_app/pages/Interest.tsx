import { Button, ButtonGroup, TextField } from "@mui/material";
import { ChessQueen, Crown, FlaskConical, Headset, Palette } from "lucide-react";

export default function Interest(props) {
    const {View, toggleView} = props;
    return(
        <div >
            <div className="text-2xl font-bold mb-4 text-center">
                <span>What is your interest?</span>
            </div>
            <div className="w-full rounded-3xl shadow-2xl p-8 bg-white text-gray-800 border-0 mt-6">
                <form className = "flex flex-col gap-4">
                    <ButtonGroup orientation="vertical" variant="text" aria-label="Vertical button group" >
                        <Button  style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} className="grid grid-cols-2 gap-4 w-full">
                            <Headset />
                            <div>Gaming</div>
                        </Button>
                        <Button style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} className="grid grid-cols-2 gap-4 w-full">
                            <FlaskConical />
                            <div>
                                Science
                            </div>
                        </Button>
                        <Button style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} className="grid grid-cols-2 gap-4 w-full">
                            <Palette />
                            <div>
                                Arts
                            </div>
                        </Button>
                        <Button style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} className="grid grid-cols-2 gap-4 w-full">
                            <ChessQueen />
                            <div>
                                Western History
                            </div>
                        </Button>
                        <Button style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'start', alignContent: 'center'}} className="grid grid-cols-2 gap-4 w-full">
                            <Crown />
                            <div>
                                Chinese History
                            </div> 
                        </Button>
                    </ButtonGroup>
                    <TextField style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px'}} 
                            id="standard-basic" 
                            label="Other..." 
                            variant="standard"
                            >
                    </TextField>
                </form>
            </div>
        <div onClick ={() => toggleView(View.HOME)} className="mt-6">
                <Button variant="contained" 
                        className="w-full text-white py-4 rounded-2xl font-bold shadow-lg shadow-teal-600/20 transition"
                        >Done!</Button>
            </div>
        </div>
    );
        
}