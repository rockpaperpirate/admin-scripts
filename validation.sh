#!/bin/bash

CYAN='\e[38;5;117m'
RESET='\e[0m'
RED='\e[38;5;167m'


input_val(){
#Usage ... [Prompt Variable] [Type of validation] [Default Value]
#Example:
#while true; do
#read -p "ENTER IP ADDR " PROMPT_VAR; echo;
#if input_val PROMPT_VAR ip 255.255.255.255; then break; fi
#done

#Trim whitespace(maybe not necessary)
local INPUT_VAL=$( sed 's/^[\s]+//;s/[\s]+$//' <<< "${!1}")

if [[ -z "${INPUT_VAL}" && -z ${3} ]]; then
    echo -e "${RED}    [!] Input is empty! ${RESET}"
    fi
    
if [[ -z "${INPUT_VAL}" && ! -z ${3} ]]; then
    echo -e "${RED}    [!] Input is empty! ${RESET}"
    echo -e "${CYAN}    [!] Setting to default, "${3}" ${RESET}"
    declare -g "$1"="${3}"
    return 0
    fi

case "${2}" in 
#IP Address
    ip|IP)
        OCTET="(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])"
        IP4="^$OCTET\\.$OCTET\\.$OCTET\\.$OCTET$"
        if [[ ! "${INPUT_VAL}" =~ ${IP4} ]]; then
            echo -e "${RED}    [!] Expecting an IP Address! ${RESET}"
            return 1
        else
            echo -e "${CYAN}    [!] Looks good! ${RESET}"
        fi
        ;;
#MAC address       
    mac|MAC)
        MAC="^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$"
        if [[ ! "${INPUT_VAL}" =~ ${MAC} ]]; then
            echo -e "${RED}    [!] Expecting a MAC Address! ${RESET}"
            return 1
        else
            echo -e "${CYAN}    [!] Looks good! ${RESET}"
        fi
        ;;
 #Number (range - use comma to separate bounds NUMA,NUMB)  
    num*|NUM*)
        RANGE=$(sed 's/^num\|^NUM//' <<< "${2}")
        LOWB=$(awk -F"," '{print $1}' <<< ${RANGE})
        UPPB=$(awk -F"," '{print $2}' <<< ${RANGE})
        #no range supplied
        if [[ -z ${RANGE} ]]; then
            if ! [[ ${INPUT_VAL} =~ ^-?[0-9]+$ ]]; then
                echo -e "${RED}    [!] Expecting a number! ${RESET}"
                return 1
            else
                echo -e "${CYAN}    [!] Looks good! ${RESET}"
                return 0
            fi
        fi
        #range supplied
        if ! (( ${INPUT_VAL} >= ${LOWB} && ${INPUT_VAL} <= ${UPPB} )); then
            echo -e "${RED}    [!] Must be between ${LOWB} and ${UPPB} ${RESET}"
            return 1
        else
            echo -e "${CYAN}    [!] Looks good! ${RESET}"
        fi
        ;;
#File       
    file|FILE)
        echo "file"
        echo "INPUT \"${INPUT_VAL}\""
        #differentiate between root and running script with sudo
        if [[ $"EUID" -eq 0 ]] then
            local HOMEPATH="/root"
        else local HOMEPATH="$HOME"
        fi
        local INPUT_VAL="$(readlink -f "${INPUT_VAL/#~/$HOMEPATH}")"
        if [[ ! -e "${INPUT_VAL}" ]]; then
            echo -e "${RED}    [!] File does not exist! ${RESET}"
            return 1
        else
			echo -e "${CYAN}    [!] Using ${INPUT_VAL} ${RESET}"
        fi
        ;;
#Directory       
    dir|DIR)
        echo "dir"
        echo "INPUT \"${INPUT_VAL}\""
        #differentiate between root and running script with sudo
        if [[ $"EUID" -eq 0 ]] then
            local HOMEPATH="/root"
        else local HOMEPATH="$HOME"
        fi
        local INPUT_VAL="$(readlink -f "${INPUT_VAL/#~/$HOMEPATH}")"
        if [[ ! -d "${INPUT_VAL}" ]]; then
            echo -e "${RED}    [!] Directory does not exist! ${RESET}"
            return 1
        else
			echo -e "${CYAN}    [!] Using ${INPUT_VAL} ${RESET}"
        fi
        ;;
    *)
        echo "everything else"
        ;;
esac
#Store any changes (primarily files)
declare -g "$1"="${INPUT_VAL}"
}

while true; do
read -e -p "What would you like to validate? " DIFF_VAR; echo;
if input_val DIFF_VAR mac de:ad:ba:be:ca:fe; then break; fi
done

