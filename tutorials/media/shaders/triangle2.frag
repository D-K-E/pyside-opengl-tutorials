#version 330 core

in mediump vec4 vertexColor;
out vec4 FragColor;

void main() {
    FragColor = vertexColor;
}
