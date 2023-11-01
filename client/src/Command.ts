//======================== Command.ts ========================
//This file contains the interfaces for server side Commands.
import { TextStyles } from "./components/Typewriter";

export enum RespType {
  Message = "MessageCommand",
  Option = "SelectOptionCommand",
  MessageDelay = "MessageDelayCommand",
  SoundDelay = "SoundDelayCommand",
}

export interface BaseCommand {
  type: RespType;
  expects_user_input: boolean;
  is_game_over: boolean;
}

export interface GenericMessageCommand extends BaseCommand {
  message: string;
  do_type_message: boolean;
  character_delay_ms: number;
}

export interface MessageCommand extends GenericMessageCommand {}

export interface SelectOptionCommand extends GenericMessageCommand {
  options: [string, string][];
}

export interface MessageDelayCommand extends GenericMessageCommand {
  delay_ms: number;
}

export interface SoundDelayCommand extends BaseCommand {
  sound_name: string;
}

export function castCommand(Command: any): BaseCommand {
  switch (Command.type) {
    case "MessageCommand":
      return Command as MessageCommand;
    case "SelectOptionCommand":
      return Command as SelectOptionCommand;
    case "MessageDelayCommand":
      return Command as MessageDelayCommand;
    case "SoundDelayCommand":
      return Command as SoundDelayCommand;
    case "SceneEndCommand":
      Command.type= "MessageCommand";
      return Command as MessageCommand;
    default:
      throw new Error("Unsupported Command type: "+Command.type);
  }
}

export function extractTextStyles(Command: BaseCommand): TextStyles {
  // Handle different types of Commands and extract styles accordingly
  switch (Command.type) {
    case "MessageCommand":
      const msgCommand = Command as GenericMessageCommand;
      var style = new TextStyles(
        msgCommand.message,
        msgCommand.do_type_message,
        msgCommand.character_delay_ms
      );
      return style;

    case "SelectOptionCommand":
      return new TextStyles("Unstyled Option");

    case "MessageDelayCommand":
      const msgDelay = Command as MessageDelayCommand;
      var style = new TextStyles(
        msgDelay.message,
        msgDelay.do_type_message,
        msgDelay.character_delay_ms
      );
      return style;

    case "SoundDelayCommand":
      //const soundDelay = Command as SoundDelay;
      return new TextStyles();
    default:
      throw new Error("Unsupported Command type");
  }
}

export function extractTextContent(Command: BaseCommand): string[] {
  // Handle different types of Commands and extract content accordingly
  switch (Command.type) {
    case "MessageCommand":
      const msgCommand = Command as MessageCommand;
      return [msgCommand.message];

    case "SelectOptionCommand":
      const optCommand = Command as SelectOptionCommand;
      return [optCommand.message].concat(
        optCommand.options.map((option) => option.join(": "))
      );

    case "MessageDelayCommand":
      const msgDelay = Command as MessageDelayCommand;
      return [msgDelay.message];

    case "SoundDelayCommand":
      //const soundDelay = Command as SoundDelay;
      return ["A Sound Is Played, check Command.tsx"];
    default:
      throw new Error("Unsupported Command type");
  }
}
