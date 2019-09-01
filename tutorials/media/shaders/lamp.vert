#version 330 core
in mediump vec3 aPos;

uniform mediump mat4 view;
uniform mediump mat4 projection;
uniform mediump mat4 model;

void main(void) 
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
