#!/bin/bash
set -e

if [ -z "$IROH_DOT_NETWORK_API_KEY" ]; then
  echo "IROH_DOT_NETWORK_API_KEY is not set. Exiting."
  exit 1
fi

# Project and Document ID
PROJECT="davidgasquez/gitcoin-grants-data-portal"
DOC_ID="m55mn6ej57fblwhtdawdlrukob6f3pmhjsge5h2n6bqsym3miaqq"

# Install sendme
curl -fsSL https://iroh.computer/sendme.sh | sh
mv sendme ~/.local/bin

# Directory containing the files
DIRECTORY="data/tables"

# Loop through each file in the directory
for FILE in "$DIRECTORY"/*; do
    echo "Processing $FILE..."

    # Add files, get ticket, and save process id
    nohup sendme send "$FILE" > ticket 2>&1 &
    echo $! > save_pid.txt

    # need to sleep long enough for the ticket to be generated
    # (bad! this won't be an issue when working with iroh as a library)
    sleep 5

    # extract hash & size from sendme output
    HASH=$(grep "hash" ticket | awk '{print $7}')
    echo "Hash: ${HASH}"

    # get file size
    SIZE=$(wc -c < "$FILE")

    # extract ticket from sendme output
    TICKET=$(grep "sendme receive" ticket | awk '{print $3}')
    echo "Ticket: ${TICKET}"

    # intiate sendme transfer to iroh.network iroh node
    echo "Uploading $FILE to iroh.network..."
    curl "https://api.iroh.network/blobs/$PROJECT" \
      -X POST \
      -H "Authorization: Bearer ${IROH_DOT_NETWORK_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"ticket\": \"${TICKET}\", \"tag\": \"latest\"}"

    # tell iroh.network to update the document entry
    echo "Updating document entry for $FILE..."
    curl "https://api.iroh.network/docs/$PROJECT/${DOC_ID}/set-hash" \
      -X POST \
      -H "Authorization: Bearer ${IROH_DOT_NETWORK_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{ \"key\": \"data\", \"hash\": \"${HASH}\", \"size\": ${SIZE} }"

    # cleanup
    kill -9 "$(cat save_pid.txt)"
    rm save_pid.txt
    rm ticket

    echo "Processed $FILE"
done

echo "All files processed"
