import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { ButtonPublic } from "@/client"
import DeleteButton from "../Buttons/DeleteButton"
import EditButton from "../Buttons/EditButton"

interface ButtonActionsMenuProps {
  button: ButtonPublic
}

export const ButtonActionsMenu = ({ button }: ButtonActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditButton button={button} />
        <DeleteButton id={button.id} />
      </MenuContent>
    </MenuRoot>
  )
}
