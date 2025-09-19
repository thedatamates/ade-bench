CREATE TABLE project_data(id VARCHAR, _fivetran_deleted BOOLEAN, _fivetran_synced TIMESTAMP, archived BOOLEAN, color VARCHAR, created_at TIMESTAMP, current_status VARCHAR, due_date TIMESTAMP, modified_at TIMESTAMP, "name" VARCHAR, notes VARCHAR, owner_id VARCHAR, public INTEGER, team_id VARCHAR, workspace_id VARCHAR);;
CREATE TABLE project_task_data(project_id VARCHAR, task_id VARCHAR, _fivetran_synced TIMESTAMP);;
CREATE TABLE section_data(id VARCHAR, _fivetran_synced TIMESTAMP, created_at TIMESTAMP, "name" VARCHAR, project_id VARCHAR);;
CREATE TABLE story_data(id VARCHAR, _fivetran_synced TIMESTAMP, created_at TIMESTAMP, created_by_id VARCHAR, hearted INTEGER, num_hearts INTEGER, source VARCHAR, target_id VARCHAR, "text" VARCHAR, "type" VARCHAR);;
CREATE TABLE tag_data(id VARCHAR, _fivetran_deleted BOOLEAN, _fivetran_synced TIMESTAMP, color INTEGER, created_at TIMESTAMP, message INTEGER, "name" VARCHAR, notes INTEGER, workspace_id VARCHAR);;
CREATE TABLE task_data(id VARCHAR, assignee_id VARCHAR, completed BOOLEAN, completed_at TIMESTAMP, completed_by_id INTEGER, created_at TIMESTAMP, due_on TIMESTAMP, due_at INTEGER, modified_at TIMESTAMP, "name" VARCHAR, parent_id INTEGER, start_on INTEGER, notes VARCHAR, workspace_id VARCHAR);;
CREATE TABLE task_follower_data(task_id VARCHAR, user_id VARCHAR, _fivetran_synced TIMESTAMP);;
CREATE TABLE task_section_data(section_id VARCHAR, task_id VARCHAR, _fivetran_synced TIMESTAMP);;
CREATE TABLE task_tag_data(tag_id VARCHAR, task_id VARCHAR, _fivetran_synced TIMESTAMP);;
CREATE TABLE team_data(id VARCHAR, _fivetran_deleted BOOLEAN, _fivetran_synced TIMESTAMP, "name" VARCHAR, organization_id VARCHAR);;
CREATE TABLE user_data(id VARCHAR, _fivetran_deleted BOOLEAN, _fivetran_synced TIMESTAMP, email VARCHAR, "name" VARCHAR);;

