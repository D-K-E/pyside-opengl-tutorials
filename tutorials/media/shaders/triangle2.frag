#version 420 core

varying mediump vec4 vertexColor;

void main() {
    gl_FragColor = vertexColor;
}
