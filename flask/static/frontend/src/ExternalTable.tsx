import { useEffect, useState } from 'react';

import axios from 'axios';
import { useQuery, useQueryClient } from '@tanstack/react-query';

import Table from './Table'


const CACHE = {};


function useTaskResult(queryKey: any, taskId: string) {
    const [result, setResult] = useState();
    console.log(taskId);

    const cacheKey = JSON.stringify(queryKey);
    const cache = CACHE[cacheKey];

    useEffect(() => {
        if (!taskId)
            return;

        if (cache) {
            const [oldTaskId, data] = cache;

            if (oldTaskId == taskId) {
                setResult(data);
                return;
            }
        }

        const socket = new WebSocket('ws://127.0.0.1:5000/sock/task/' + taskId);
        socket.onmessage = message => {
            const data = JSON.parse(message.data);
            setResult(data);
            CACHE[cacheKey] = [taskId, data];
        }

        return () => {
            socket.close();
        }
    }, [taskId])

    return result;
}

function ExternalTable({name}: {name: string}) {
    const queryKey = ['table', name];

    const { isLoading, data } = useQuery(
        queryKey,
        () => axios.get(`http://localhost:5000/api/db/${name}/5`)
                   .then(response => response.data)
                   .then(data => data['result_id'])
    );

    //const result = data;

    const result = useTaskResult(queryKey, data);
    console.log(result)

    if (!result)
        return null;

    return <Table rows={result.result} />;
}


export default ExternalTable;
