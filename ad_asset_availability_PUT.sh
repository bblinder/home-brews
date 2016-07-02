#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

asset_store_legacy="[legacy asset store]"
asset_store_watermark="[modern asset store]"

staging_environment='[staging]'
prod_environment='[production]'

# Probably a simpler way to do this...
BUILD_URL_STAGING(){

	LEGACY(){
		curl -H "Accept: application/xml" \
			-H "Content-Type: application/xml" \
			-H "X-[Token_type]: $api_token" \
			-X PUT "$staging_environment/services/ad_asset_store/$network_id" \
			-d "<asset><tag>$asset_store_legacy</tag><url>$URI</url><available_percentage>100</available_percentage></asset>"
	}

	WATERMARK(){
		curl -H "Accept: application/xml" \
			-H "Content-Type: application/xml" \
			-H "X-[Token-type]: $api_token" \
			-X PUT "$staging_environment/services/ad_asset_store/$network_id" \
			-d "<asset><tag>$asset_store_watermark</tag><url>$URI</url><available_percentage>100</available_percentage></asset>"
	}

	if [[ "$URI" == vod* ]] ; then
		read -rp "Asset Store? Cox Legacy (1) or Watermark (2) or Both (3)  " asset_store_choice
		case "$asset_store_choice" in

			1)
				LEGACY
				;;

			2)
				WATERMARK
				;;

			3)
				LEGACY
				WATERMARK
				;;

			*)
				echo "Please pick (1) or (2) or (3)"
				;;

		esac
	else
		echo "Not a valid PID/PAID URI"
	fi
}

BUILD_URL_PROD(){

	LEGACY(){
		curl -H "Accept: application/xml" \
			-H "Content-Type: application/xml" \
			-H "X-[Token-type]: $api_token" \
			-X PUT "$prod_environment/services/ad_asset_store/$network_id" \
			-d "<asset><tag>$asset_store_legacy</tag><url>$URI</url><available_percentage>100</available_percentage></asset>"
	}

	WATERMARK(){
		curl -H "Accept: application/xml" \
			-H "Content-Type: application/xml" \
			-H "X-[Token-type]: $api_token" \
			-X PUT "$prod_environment/services/ad_asset_store/$network_id" \
			-d "<asset><tag>$asset_store_watermark</tag><url>$URI</url><available_percentage>100</available_percentage></asset>"
	}

	if [[ "$URI" == vod* ]] ; then
		read -rp "Asset Store? Cox Legacy (1) or Watermark (2) or Both (3)   " asset_store_choice
		case "$asset_store_choice" in

			1)
				LEGACY
				;;

			2)
				WATERMARK
				;;

			3)
				LEGACY
				WATERMARK
				;;

			*)
				echo "Please pick (1) or (2) or (3)"
				;;
		esac
	else
		echo "Not a valid PID/PAID URI"
	fi
}

# Now onto the actual work...
read -rp "Network ID:  " network_id
if [[ ! $network_id ]] ; then
	echo "Please enter Network ID"
	exit 1
fi

read -rp "Environment? Staging (1) or Production (2)   " environment_choice
case "$environment_choice" in
	1)
		read -rp "API token: " api_token
		read -rp "Enter URI: " URI

		BUILD_URL_STAGING
		;;

	2)
		read -rp "API token " api_token
		read -rp "Enter URI: " URI

		BUILD_URL_PROD
		;;

	*)
		echo "Enter Staging (1) or Production (2)"
		;;
esac
