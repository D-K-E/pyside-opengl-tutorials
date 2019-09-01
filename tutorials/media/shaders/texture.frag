#version 330 core
in highp vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D myTexture;

void main(void)
{
    FragColor = texture(myTexture, TexCoord);
}
