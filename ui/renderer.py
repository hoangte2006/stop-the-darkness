"""Draws the game board using TV2's sprite art."""

import pygame

SPRITE_DIR = "assets/images/ui/sprites"

SPRITE_FILES = {
    "grass": "ground/ground.png",
    "forest": "trees/tree-3.png",
    "water": "water/water.png",
    "rock": "stone/stone-3.png",
    "building": "structure/building-3.png",
    "darkness": "darkness/darkness.png",
}


class TileMapRenderer:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.sprites = {}

    def load_sprites(self):
        """Nap tat ca sprite 1 lan luc dau, luu vao self.sprites theo ten."""
        for key, relative_path in SPRITE_FILES.items():
            full_path = f"{SPRITE_DIR}/{relative_path}"
            image = pygame.image.load(full_path).convert_alpha()
            image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
            self.sprites[key] = image

    def sprite_key_for_tile(self, tile):
        """Quyet dinh 1 Tile that nen ve bang sprite nao."""
        if tile.is_dark:
            return "darkness"
        if tile.building is not None:
            return "building"
        return tile.terrain  # "grass" | "forest" | "water" | "rock"

    def draw(self, screen, game):
        """Ve toan bo game.grid len screen, dung dung sprite cho tung o."""
        for row in game.grid:
            for tile in row:
                key = self.sprite_key_for_tile(tile)
                sprite = self.sprites[key]
                x = tile.col * self.tile_size
                y = tile.row * self.tile_size
                screen.blit(sprite, (x, y))
