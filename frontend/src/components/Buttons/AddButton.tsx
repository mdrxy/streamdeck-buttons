import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type ButtonCreate, ButtonsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddButton = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<ButtonCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      type: "PSA",
      description: null,
      duration: null,
      source: null
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ButtonCreate) =>
      ButtonsService.createButton({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Button created successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["buttons"] })
    },
  })

  const onSubmit: SubmitHandler<ButtonCreate> = (data) => {
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
        <Button value="add-button" my={4}>
          <FaPlus fontSize="16px" />
          Add Button
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add Button</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new button.</Text>
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
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddButton
