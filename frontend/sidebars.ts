import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'part1-foundations/module1-intro',
        'part1-foundations/module1-chapter1',
        'part1-foundations/module1-chapter2',
        'part1-foundations/module1-chapter3',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'part2-perception/module2-intro',
        'part2-perception/module2-chapter1',
        'part2-perception/module2-chapter2',
        'part2-perception/module2-chapter3',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'part3-cognition/module3-intro',
        'part3-cognition/module3-chapter1',
        'part3-cognition/module3-chapter2',
        'part3-cognition/module3-chapter3',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'part4-action/module4-intro',
        'part4-action/module4-chapter1',
        'part4-action/module4-chapter2',
        'part4-action/module4-chapter3',
      ],
    },
    {
      type: 'category',
      label: 'Tutorial',
      items: [
        'intro',
        'tutorial-basics/create-a-document',
        'tutorial-basics/create-a-blog-post',
        'tutorial-basics/create-a-page',
        'tutorial-basics/markdown-features',
        'tutorial-basics/congratulations',
      ],
    },
  ],
};

export default sidebars;
