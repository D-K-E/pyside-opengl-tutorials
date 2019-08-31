#version 330 core
attribute mediump vec3 aPos;
attribute mediump vec3 aNormal;
attribute mediump vec2 aTexCoord;

out mediump vec3 Normal;
out mediump vec2 TexCoords;
out mediump vec3 FragPos;

uniform highp mat4 model;
uniform highp mat4 view;
uniform highp mat4 projection;

void main(void)
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoords = aTexCoord;
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
