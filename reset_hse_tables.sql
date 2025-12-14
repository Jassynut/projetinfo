-- Script SQL pour supprimer les tables HSE et réinitialiser les migrations
-- ATTENTION: Ce script supprime TOUTES les données des tables HSEUser et HSEManager

-- 1. Supprimer les tables (CASCADE supprime aussi les contraintes de clé étrangère)
DROP TABLE IF EXISTS hse_app_hseuser CASCADE;
DROP TABLE IF EXISTS hse_app_hsemanager CASCADE;

-- 2. Supprimer les entrées de migration de Django
DELETE FROM django_migrations WHERE app = 'hse_app';

-- Vérification
SELECT 'Tables supprimées avec succès!' AS message;


