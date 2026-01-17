import { useState } from "react";
import CoursesView from "./Courses";
import CourseExpandedView from "./CourseExpanded";

export default function LearnView (props) {
    const { notify } = props;
    const [lessonId, setLessonId] = useState<string | null>(null);
    const [isExpanded, setIsExpanded] = useState(false);

    const toggleLessonDetails = (id: string) => {
        setLessonId(id === lessonId ? null : id);
        setIsExpanded(true);
    };

    const closeLessonDetails = () => {
        setLessonId(null);
        setIsExpanded(false);
    };

    return(
        <div>
            {!isExpanded && <CoursesView toggleLessonDetails={toggleLessonDetails}/>}
            {isExpanded && <CourseExpandedView lessonId={lessonId} closeLessonDetails={closeLessonDetails} notify={notify}/>}
        </div>
    )
}