#version 330 core
in highp vec3 aPos;

out mediump vec4 vertexColor;

void main() {
    gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
    vertexColor = vec4(0.1, 0.3, 0.8, 1.0);
}
