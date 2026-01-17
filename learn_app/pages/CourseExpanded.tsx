import { ChevronLeft } from "lucide-react";

export default function CourseExpandedView(props) {
    const {lessonId, closeLessonDetails} = props;
    return(
        <div>
            <ChevronLeft onClick={closeLessonDetails} />
            <h1>Course Expanded View {lessonId}</h1>
        </div>
    )
}