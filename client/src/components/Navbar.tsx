import { Box, Flex, Heading, Spacer, Badge } from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface WorkerCountResponse {
  count: number
}

const Navbar = () => {
  const { data: workerCount, isError, isInitialLoading } = useQuery({
    queryKey: ['workerCount'],
    queryFn: async () => {
      try {
        const response = await axios.get<WorkerCountResponse>('http://localhost:8000/workers/count')
        return response.data.count
      } catch (error) {
        throw error
      }
    },
    refetchInterval: 5000,
    retry: 0,
    initialData: undefined
  })

  let status: string
  let color: string

  if (isInitialLoading) {
    status = "Connecting..."
    color = "gray"
  } else if (isError) {
    status = "Offline"
    color = "red"
  } else if (workerCount && workerCount > 0) {
    status = `${workerCount} worker${workerCount > 1 ? 's' : ''}`
    color = "green"
  } else {
    status = "Idle"
    color = "yellow"
  }

  return (
    <Box bg="white" px={4} py={4} shadow="sm">
      <Flex maxW="container.xl" mx="auto" alignItems="center">
        <Heading size="md">Distributed Processing System</Heading>
        <Spacer />
        <Badge colorScheme={color} variant="subtle" px={2} py={1}>
          {status}
        </Badge>
      </Flex>
    </Box>
  )
}

export default Navbar