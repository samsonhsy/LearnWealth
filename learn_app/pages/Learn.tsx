import { BrainCircuit } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchData } from "../api";

export default function LearnView () {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      fetchData('/course_content/admin/courses/')
        .then(data => {
          setData(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err);
          setLoading(false);
        });
    }, []);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error loading data!</p>;
    return (
    <div className="p-4 pb-24 space-y-6">
      
      <div className="space-y-4 lg:space-y-0 lg:grid lg:grid-cols-3 lg:gap-4 lg:justify-center lg:items-center">
        This is the Learn page.
        <pre>{JSON.stringify(data, null, 2)}</pre>
        <p>{data}</p>
      </div>
    </div>
  );
}