IMAGE_NAME="gmail-autopdf"

echo "Building image: $IMAGE_NAME..."

sudo docker build -t $IMAGE_NAME ./backend

# Verificar si la construcción fue exitosa
if [ $? -eq 0 ]; then
    echo "Succesful build."
    
    echo "Cleaning previous images..."
    sudo docker image prune -f --filter "dangling=true"
    
    echo "Executing container..."
    
    sudo docker run --rm --env-file .env.secrets -v "$HOME/.config/rclone/rclone.conf:/root/.config/rclone/rclone.conf" -v "$(pwd)/backend/backup_todos.mbox:/code/backup_todos.mbox" -v "$(pwd)/backend/received_messages.txt:/code/received_messages.txt" -v "$(pwd)/output:/code/output" $IMAGE_NAME 


else
    echo "Fail running image."
    exit 1
fi

