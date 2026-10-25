
import { useState } from 'react';
import Header from './components/Header';
import PatientTable from './components/PatientTable';
import type { Encounter } from './types';
import './App.css';
import Pagination from './components/Pagination';
import useApi from './hooks/useApi';

const PAGE_SIZE = 10;

function App() {
    const { data, error, isLoading } = useApi<Encounter[]>('http://127.0.0.1:8001/encounters');
    const encounters = data ?? [];
    const [currentPage, setCurrentPage] = useState(1);
    const totalPages = Math.max(1, Math.ceil(encounters.length / PAGE_SIZE));
    const page = Math.min(currentPage, totalPages);
    const startIndex = (page - 1) * PAGE_SIZE;
    const paginatedEncounters = encounters.slice(startIndex, startIndex + PAGE_SIZE);

    return (
        <div className="App">
            <Header />
            {isLoading && <p role="status">Loading encounters...</p>}
            {error && <p role="alert">{error.message}</p>}
            <PatientTable encounters={paginatedEncounters} />
            <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
            />
        </div>

    );
}
export default App;