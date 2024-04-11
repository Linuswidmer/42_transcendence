#!/bin/bash
echo "setup_users.sh: Start"

# Check if the user exists
user_exists=$(psql -U pong_user -d postgres -t -c "SELECT 1 FROM auth_user WHERE username = 'linus'")
ursula_exists=$(psql -U pong_user -d postgres -t -c "SELECT 1 FROM auth_user WHERE username = 'AI_Ursula'")
local_exists=$(psql -U pong_user -d postgres -t -c "SELECT 1 FROM auth_user WHERE username = 'DUMP_LOCAL'")

# If the user does not exist, insert the new user
if [ -z "$user_exists" ]; then
    psql -U pong_user -d postgres -c "
    INSERT INTO auth_user (is_superuser, first_name, last_name, email, is_staff, is_active, date_joined,  username, password) VALUES (false, 'linus', 'w', 'linus@ping.pong', false, 'false', '01-01-1970',  'linus', '123');
    "
else
    echo "User 'linus' already exists."
fi

if [ -z "$ursula_exists" ]; then
    psql -U pong_user -d postgres -c "
    INSERT INTO auth_user (is_superuser, first_name, last_name, email, is_staff, is_active, date_joined,  username, password) VALUES (false, 'AI', 'Ursula', 'me@me.com', false, 'false', '01-01-1970',  'AI_Ursula', '123');
    "
else
    echo "User 'AI_Ursula' already exists."
fi

if [ -z "$local_exists" ]; then
    psql -U pong_user -d postgres -c "
    INSERT INTO auth_user (is_superuser, first_name, last_name, email, is_staff, is_active, date_joined,  username, password) VALUES (false, 'DUMP', 'LOCAL', 'me@me.com', false, 'false', '01-01-1970',  'DUMP_LOCAL', '123');
    "
else
    echo "User 'DUMP_LOCAL' already exists."
fi


echo "setup_users.sh: Done"