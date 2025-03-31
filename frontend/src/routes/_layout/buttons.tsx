import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { ButtonsService } from "@/client"
import { ButtonActionsMenu } from "@/components/Common/ButtonActionsMenu"
import AddButton from "@/components/Buttons/AddButton"
import PendingButtons from "@/components/Pending/PendingButtons"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const buttonsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getButtonsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ButtonsService.listAllButtons({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["buttons", { page }],
  }
}

export const Route = createFileRoute("/_layout/buttons")({
  component: Buttons,
  validateSearch: (search) => buttonsSearchSchema.parse(search),
})

function ButtonsTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getButtonsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const buttons = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingButtons />
  }

  if (buttons.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>No buttons have been added yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new button to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Title</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {buttons?.map((button) => (
            <Table.Row key={button.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {button.id}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {button.title}
              </Table.Cell>
              <Table.Cell
                color={!button.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {button.description || "N/A"}
              </Table.Cell>
              <Table.Cell>
                <ButtonActionsMenu button={button} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Buttons() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Button Management
      </Heading>
      <AddButton />
      <ButtonsTable />
    </Container>
  )
}
