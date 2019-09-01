#version 330 core
in mediump vec3 aPos;
in mediump vec3 aNormal;
in mediump vec2 aTexCoord;

out mediump vec3 Normal;
out mediump vec2 TexCoords;
out mediump vec3 FragPos;

uniform highp mat4 model;
uniform highp mat4 view;
uniform highp mat4 projection;

void main(void)
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    TexCoords = aTexCoord;
}
