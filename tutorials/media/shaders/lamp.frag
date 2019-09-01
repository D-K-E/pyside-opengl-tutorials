#version 330 core
uniform lowp vec3 color;
out vec4 FragColor;

void main(void)
{
    FragColor = vec4(color, 1.0);
}
