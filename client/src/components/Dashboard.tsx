import React from 'react'
import {
  Box,
  Grid,
  GridItem,
  VStack,
  Button,
  Input,
  Text,
  useToast,
  Progress,
  Card,
  CardHeader,
  CardBody,
  Heading,
} from '@chakra-ui/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

interface Task {
  id: number
  input_data: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result: Record<string, any> | null
  created_at: string
  updated_at: string
  worker_id: string | null
}

const Dashboard = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const [inputData, setInputData] = React.useState('')

  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      try {
        const response = await axios.get<Task[]>('http://localhost:8000/tasks')
        return response.data
      } catch (error) {
        console.error('Error fetching tasks:', error)
        return []
      }
    },
    refetchInterval: 2000,
    refetchIntervalInBackground: true,
  })

  const submitTask = useMutation({
    mutationFn: async (data: string) => {
      const response = await axios.post<Task>('http://localhost:8000/tasks', {
        input_data: data,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast({
        title: 'Task submitted',
        status: 'success',
        duration: 3000,
      })
      setInputData('')
    },
  })

  return (
    <Grid templateColumns="repeat(2, 1fr)" gap={8}>
      <GridItem>
        <Card>
          <CardHeader>
            <Heading size="md">Submit New Task</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Input
                value={inputData}
                onChange={(e) => setInputData(e.target.value)}
                placeholder="Enter data to process..."
              />
              <Button
                colorScheme="blue"
                onClick={() => submitTask.mutate(inputData)}
                isLoading={submitTask.isPending}
                width="full"
              >
                Submit Task
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </GridItem>

      <GridItem>
        <Card>
          <CardHeader>
            <Heading size="md">Task Monitor</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {isLoadingTasks ? (
                <Text color="gray.500" textAlign="center">Loading tasks...</Text>
              ) : tasks.length === 0 ? (
                <Text color="gray.500" textAlign="center">
                  No tasks submitted yet
                </Text>
              ) : (
                tasks.map((task: Task) => (
                  <Box key={task.id} p={4} borderWidth={1} borderRadius="md">
                    <Text fontWeight="bold">Task ID: {task.id}</Text>
                    <Text>Input: {task.input_data}</Text>
                    <Progress
                      mt={2}
                      value={task.status === 'completed' ? 100 : task.status === 'processing' ? 50 : 0}
                      colorScheme={
                        task.status === 'completed'
                          ? 'green'
                          : task.status === 'processing'
                          ? 'blue'
                          : 'gray'
                      }
                    />
                    <Text mt={2} color="gray.600">
                      Status: {task.status}
                    </Text>
                    {task.result && (
                      <Text mt={2}>Result: {JSON.stringify(task.result)}</Text>
                    )}
                  </Box>
                ))
              )}
            </VStack>
          </CardBody>
        </Card>
      </GridItem>
    </Grid>
  )
}

export default Dashboard 