import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type ButtonPublic, ButtonsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditButtonProps {
  button: ButtonPublic
}

interface ButtonUpdateForm {
  title: string
  description?: string
}

const EditButton = ({ button }: EditButtonProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ButtonUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...button,
      description: button.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ButtonUpdateForm) =>
      ButtonsService.updateButton({ id: button.id, requestBody: data }),
    onSuccess: (_data: ButtonPublic, variables: ButtonUpdateForm) => {
      showSuccessToast("Button updated successfully.")
      reset(variables)
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["buttons"] })
    },
  })

  const onSubmit: SubmitHandler<ButtonUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit Button
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Button</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the button details below.</Text>
            <VStack gap={4}>
              <Field
                invalid={!!errors.type}
                errorText={errors.type?.message}
                label="Type"
              >
                <Input
                  id="type"
                  {...register("type", {
                    required: "Type is required.",
                  })}
                  placeholder="Type"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.title}
                errorText={errors.title?.message}
                label="Title"
              >
                <Input
                  id="title"
                  {...register("title", {
                    required: "Title is required.",
                  })}
                  placeholder="Title"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  id="description"
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.source}
                errorText={errors.source?.message}
                label="Source"
              >
                <Input
                  id="source"
                  {...register("source")}
                  placeholder="Source"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.duration}
                errorText={errors.duration?.message}
                label="Duration"
              >
                <Input
                  id="duration"
                  {...register("duration", {
                    valueAsNumber: true,
                    validate: {
                      isPositive: (value) =>
                        (value != null && Number(value) > 0) || "Duration must be a positive number.",
                    },
                  })}
                  placeholder="Duration"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditButton
