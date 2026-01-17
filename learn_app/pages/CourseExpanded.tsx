
import { fetchData, postData } from "@/api";
import { ChevronLeft } from "lucide-react";
import { useEffect, useState, CSSProperties } from "react";
import Box from '@mui/material/Box';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import StepContent from '@mui/material/StepContent';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import React from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { ButtonGroup } from "@mui/material";
import { ClipLoader } from "react-spinners";

const override: CSSProperties = {
  display: "block",
  margin: "0 auto",
  borderColor: "red",
};

export function QuizView(props) {
    const { toggleQuiz, sectionId, notify, isExplanation, setIsExplanation } = props;
    const [data, setData] = useState<{ sections?: any[] }>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [startQuiz, setStartQuiz] = useState(false);
    const [answer, setAnswer] = useState<string>('');
    console.log("Selected answer:", answer);


    const completeQuiz = async () => {
        try {
            const response = await postData(`/student/student/section/${sectionId}/submit?correct=true`);
            console.log("Quiz completed:", response);
        } catch (error) {
            console.error("Error completing quiz:", error);
        }
    }

    const checkanswer = () => {
        if (answer === '') {
            notify("Please select an answer before submitting.", 'error');
            return;
        }
        if (answer === data.quiz.correct_answer) {
            notify("Correct answer!", 'success');
            setIsExplanation(true);
        } else {
            notify("Wrong answer. Try again!", 'error');
        }
    };

    useEffect(() => {
        let cancelled = false;
        let timeoutId: number | undefined;

        const pollEnroll = async () => {
          try {
            const res = await fetchData(`/student/student/section/${sectionId}/content`);
            // assume res.data or res has status field — adapt to your API shape
            const status = res?.data?.status ?? res?.status ?? null;
            console.log("Enroll poll response:", res);

            if (status === "ready" || status === "enrolled") {
              setData(res)
              console.log("Ready received — stop polling");
              setLoading(false);
              return;
            }
        
            if (!cancelled) {
              // schedule next poll after 2s
              timeoutId = window.setTimeout(pollEnroll, 10000);
            }
          } catch (err) {
            setError(err);
            setLoading(false);
            // optionally stop on error or retry:
            if (!cancelled) timeoutId = window.setTimeout(pollEnroll, 10000);
          }
        };
    
        pollEnroll();
    
        return () => {
          cancelled = true;
          if (timeoutId) clearTimeout(timeoutId);
        };
    }, [sectionId]);

    if (loading) return <div className="fixed inset-0 flex items-center justify-center bg-white">
                            <ClipLoader 
                                color="#009689" 
                                loading={loading} 
                                size={150} 
                                aria-label="Loading Spinner" 
                                data-testid="loader" />
                        </div>
    if (error) return <p>Error loading data!</p>;

    return (isExplanation? (
        <div>
            <div className="mt-6 text-2xl flex flex-col gap-6 items-center" style={{width: '100%'}}>
                <div className="flex flex-col mt-6">
                    <div className="mt-6">Correct Answer: {data.quiz.correct_answer}</div>
                    <div className="mt-6">Explanation: </div>
                    <div className="mt-6">{data.quiz.explanation}</div>
                </div>
            </div>
            <Button
                variant="contained"
                fullWidth
                style={{width: '100%', marginTop: '30px', height: '50px', fontSize: '18px'}}
                onClick={()=>{
                    {toggleQuiz(), setIsExplanation(false), setStartQuiz(false), setAnswer(''), completeQuiz()};
                }}
            >Close Quiz</Button>
        </div>) :(!startQuiz ? ( 
        <div className="mt-6 text-2xl flex flex-col gap-6 items-center" style={{width: '100%'}}>
            <div>
                <ReactMarkdown>{data.content}</ReactMarkdown>
                <Button
                    variant="contained"
                    fullWidth
                    style={{width: '100%', marginTop: '30px', height: '50px', fontSize: '18px'}}
                    onClick={()=>setStartQuiz(true)}
                >Start Quiz</Button>
            </div>
        </div>) : (
        <div className="mt-6 text-2xl flex flex-col gap-6 items-center" style={{width: '100%'}}>
            <div>
                {data.quiz.question? 
                    <div>
                        <div>{data.quiz.question}</div>
                        <div className="mt-10 w-full flex flex-col justify-center">
                            <ButtonGroup orientation="vertical" variant="text" aria-label="Vertical button group" style={{width:'100%'}}>
                                {data.quiz.options.map((option, idx) => (   
                                    <Button
                                        key={idx}
                                        variant={answer === option ? "contained" : "outlined"}
                                        style={{maxHeight: '300px', minHeight: '50px', fontSize: '14px', justifyContent: 'center', alignContent: 'center', width: '100%'}}
                                        onClick={() => setAnswer(option)}
                                    >{option}</Button>
                                ))}
                            </ButtonGroup>
                            <Button
                                variant="contained"
                                fullWidth
                                style={{width: '100%', marginTop: '30px', height: '50px', fontSize: '18px'}}
                                onClick={() => checkanswer()}>
                                Submit
                            </Button>
                        </div>
                    </div>
                    : <div>No quiz available.</div>
                }
            </div>
        </div>)
        )
    );
}

export function SectionsPath(props) {

    const {lessonId,setSectionId, toggleQuiz} = props;
    const [data, setData] = useState<{ sections?: any[] }>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeStep, setActiveStep] = React.useState(0);

    useEffect(() => {
        let cancelled = false;
        let timeoutId: number | undefined;

        const pollEnroll = async () => {
          try {
            const res = await postData(`/student/student/course/${lessonId}/enroll`);
            fetchData(`/student/student/course/${lessonId}`)
            .then(data => {
                setData(data && typeof data === "object" ? data : {});
                console.log("Fetched course data:", data);
                setLoading(false);
            })
            .catch(err => {
                setError(err);
                setLoading(false);
            });
            // assume res.data or res has status field — adapt to your API shape
            const status = res?.data?.status ?? res?.status ?? null;
            console.log("Enroll poll response:", res);

            if (status === "ready" || status === "enrolled") {
              console.log("Ready received — stop polling");
              return;
            }
        
            if (!cancelled) {
              // schedule next poll after 2s
              timeoutId = window.setTimeout(pollEnroll, 10000);
            }
          } catch (err) {
            setError(err);
            setLoading(false);
            // optionally stop on error or retry:
            if (!cancelled) timeoutId = window.setTimeout(pollEnroll, 10000);
          }
        };
    
        pollEnroll();
    
        return () => {
          cancelled = true;
          if (timeoutId) clearTimeout(timeoutId);
        };
    }, [lessonId]);
    if (loading) return <div className="fixed inset-0 flex items-center justify-center bg-white">
                            <ClipLoader 
                                color="#009689" 
                                loading={loading} 
                                size={150} 
                                aria-label="Loading Spinner" 
                                data-testid="loader" />
                        </div>
    if (error) return <p>Error loading data!</p>;
    if (!Array.isArray(data.sections)) return null;

    const theme = createTheme({typography: {fontSize: 18}});

    const handleNext = () => {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };

    const handleBack = () => {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleReset = () => {
      setActiveStep(0);
    };
    return (
        <div>
            <div className="ml-2 mt-6">{data.course}</div>
            <Box sx={{ maxWidth: 400, ml: 4}}>
                <ThemeProvider theme={theme}>

                    <Stepper activeStep={activeStep} orientation="vertical">
                        {data.sections.map(({id, is_completed, is_locked, title}, index) => (
                        <Step key={id}>
                            <StepLabel
                            style={{fontSize: '32px'}}
                            >
                            {title}
                            </StepLabel>
                            <StepContent>
                            <Box sx={{ mb: 2, flexDirection: 'column', display: 'flex', width: '80%' }}>
                                <Button 
                                    disabled={is_locked}
                                    variant="contained"
                                    onClick={() => {toggleQuiz(); setSectionId(id);}}>
                                    Start Section
                                </Button>
                                <Button
                                disabled={!is_completed}
                                variant="contained"
                                onClick={handleNext}
                                sx={{ mt: 1, mr: 1 }}
                                >
                                    {is_completed? 'Next Section': 'Not Completed'}
                                </Button>
                                {  index == 0 ? null : 
                                <Button
                                disabled = {data.sections[id - 1]?.is_locked}
                                onClick={handleBack}
                                sx={{ mt: 1, mr: 1 }}
                                >
                                    Back 
                                </Button>}
                            </Box>
                            </StepContent>
                        </Step>
                        ))}
                    </Stepper>
                    {activeStep === data.sections.length && (
                        <Paper square elevation={0} sx={{ p: 3 }}>
                        <Typography>All Sections Completed, Well Done!</Typography>
                        <Button variant="contained" onClick={handleReset} sx={{ mt: 1, mr: 1 }}>
                            Back to Top
                        </Button>
                        </Paper>
                    )}
                </ThemeProvider>
            </Box>
        </div>
    );
}

export default function CourseExpandedView(props) {
    const {lessonId,notify, closeLessonDetails} = props;
    const [isQuizOpen, setIsQuizOpen] = useState(false);
    const [sectionId, setSectionId] = useState<string | null>(null);
    const [isExplanation, setIsExplanation] = useState(false);
    
    const toggleQuiz = () => {
        setIsQuizOpen(!isQuizOpen);
    };

    return(
        <div className="text-2xl ml-4 mb-22" style={{width: '95%'}}>
            {!isExplanation && <ChevronLeft onClick={isQuizOpen? toggleQuiz: closeLessonDetails} size={30} className="mt-6 text-gray-500 "/>}
            {!isQuizOpen && 
                <div>
                    <SectionsPath className="mt-6" lessonId={lessonId} setSectionId={setSectionId} toggleQuiz={toggleQuiz}/>
                </div>
            }
            {isQuizOpen && <QuizView toggleQuiz={toggleQuiz} sectionId={sectionId} notify={notify} isExplanation={isExplanation} setIsExplanation={setIsExplanation}/>}
        </div>
    )
}